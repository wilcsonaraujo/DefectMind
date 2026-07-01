import { createFileRoute, useSearch, useNavigate } from "@tanstack/react-router";
import { useCallback, useEffect, useLayoutEffect, useRef, useState } from "react";
import { z } from "zod";
import {
  ReactFlow,
  Background,
  Controls,
  MiniMap,
  useNodesState,
  useEdgesState,
  type Node,
  type Edge,
  MarkerType,
  Panel,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import { Loader2, Network, AlertCircle, Search } from "lucide-react";
import { AppLayout } from "@/components/app-layout";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { getImpactAnalysis, type ImpactNode, type EntityType } from "@/lib/api";
import { useLang } from "@/lib/i18n";

// ─── Validação de query string ────────────────────────────────────────────────
const searchSchema = z.object({
  nodeId: z.string().optional(),
});

export const Route = createFileRoute("/impact")({
  validateSearch: searchSchema,
  head: () => ({
    meta: [
      { title: "Análise de Impacto — DefectMind" },
      {
        name: "description",
        content: "Analise o raio de impacto de um artefato no grafo do DefectMind.",
      },
    ],
  }),
  component: ImpactPage,
});

// ─── Mapa de cores por tipo de artefato ──────────────────────────────────────
const NODE_COLORS: Record<EntityType | string, { bg: string; border: string; text: string }> = {
  Story:       { bg: "#1d4ed8", border: "#3b82f6", text: "#ffffff" },
  BugReport:   { bg: "#b91c1c", border: "#ef4444", text: "#ffffff" },
  TestCase:    { bg: "#15803d", border: "#22c55e", text: "#ffffff" },
  Requirement: { bg: "#7e22ce", border: "#a855f7", text: "#ffffff" },
  Incident:    { bg: "#c2410c", border: "#f97316", text: "#ffffff" },
  PostMortem:  { bg: "#374151", border: "#6b7280", text: "#ffffff" },
};

const DEFAULT_COLOR = { bg: "#1e293b", border: "#475569", text: "#ffffff" };

// ─── Algoritmo de layout em grade (sem dependência externa) ───────────────────
function applyGridLayout(
  nodes: ImpactNode[],
  rootId: string,
): { id: string; x: number; y: number }[] {
  const NODE_W = 180;
  const NODE_H = 60;
  const H_GAP = 60;
  const V_GAP = 80;

  // Coloca o nó raiz no centro e distribui os demais em colunas
  const root = nodes.find((n) => n.id === rootId);
  const others = nodes.filter((n) => n.id !== rootId);

  const cols = Math.ceil(Math.sqrt(others.length + 1));
  const positions: { id: string; x: number; y: number }[] = [];

  // Nó raiz no topo ao centro
  const centerX = ((cols - 1) / 2) * (NODE_W + H_GAP);
  positions.push({ id: rootId, x: centerX, y: 0 });

  others.forEach((n, i) => {
    const col = i % cols;
    const row = Math.floor(i / cols) + 1;
    positions.push({
      id: n.id,
      x: col * (NODE_W + H_GAP),
      y: row * (NODE_H + V_GAP),
    });
  });

  return positions;
}

// ─── Componente principal ─────────────────────────────────────────────────────
function ImpactPage() {
  const { t } = useLang();
  const navigate = useNavigate({ from: "/impact" });
  const { nodeId: initialNodeId } = useSearch({ from: "/impact" });

  const [nodeIdInput, setNodeIdInput] = useState(initialNodeId ?? "");
  const [depth, setDepth] = useState("3");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [searched, setSearched] = useState(false);

  // Estado do React Flow
  const [rfNodes, setRfNodes, onNodesChange] = useNodesState<Node>([]);
  const [rfEdges, setRfEdges, onEdgesChange] = useEdgesState<Edge>([]);

  // Modal de detalhes
  const [selectedNode, setSelectedNode] = useState<ImpactNode | null>(null);
  const rawNodesRef = useRef<ImpactNode[]>([]);

  // ─── Dispara busca automática se nodeId vier pela query string ────────────
  useEffect(() => {
    if (initialNodeId) {
      setNodeIdInput(initialNodeId);
      handleSearch(initialNodeId, "3");
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // ─── Função de busca ──────────────────────────────────────────────────────
  const handleSearch = useCallback(
    async (id?: string, d?: string) => {
      const targetId = (id ?? nodeIdInput).trim();
      const targetDepth = parseInt(d ?? depth, 10);

      if (!targetId) return;

      setLoading(true);
      setError(null);
      setSearched(true);
      setRfNodes([]);
      setRfEdges([]);

      // Atualiza a query string sem recarregar a página
      navigate({ search: { nodeId: targetId }, replace: true });

      try {
        const data = await getImpactAnalysis(targetId, targetDepth);
        rawNodesRef.current = data.nodes;

        if (data.nodes.length === 0) {
          setError("Nenhum nó encontrado para este ID. Verifique se o artefato existe no grafo.");
          return;
        }

        // Calcular posições
        const positions = applyGridLayout(data.nodes, targetId);
        const posMap = new Map(positions.map((p) => [p.id, p]));

        // Construir nós do React Flow
        const flowNodes: Node[] = data.nodes.map((n) => {
          const color = NODE_COLORS[n.label] ?? DEFAULT_COLOR;
          const pos = posMap.get(n.id) ?? { x: 0, y: 0 };
          const title =
            (n.properties.title as string) ??
            (n.properties.description as string)?.slice(0, 40) ??
            n.id.slice(0, 12) + "…";
          const isRoot = n.id === targetId;

          return {
            id: n.id,
            position: { x: pos.x, y: pos.y },
            data: { label: `${n.label}\n${title}` },
            style: {
              background: color.bg,
              border: `2px solid ${color.border}`,
              color: color.text,
              borderRadius: "8px",
              padding: "8px 12px",
              fontSize: "11px",
              fontWeight: isRoot ? 700 : 400,
              boxShadow: isRoot ? `0 0 0 3px ${color.border}55` : undefined,
              whiteSpace: "pre-line",
              textAlign: "center",
              minWidth: "140px",
            },
          };
        });

        // Construir arestas do React Flow
        const flowEdges: Edge[] = data.edges.map((e, i) => ({
          id: `e-${i}`,
          source: e.source,
          target: e.target,
          label: e.relation,
          labelStyle: { fontSize: "9px", fill: "#94a3b8" },
          labelBgStyle: { fill: "#0f172a", fillOpacity: 0.8 },
          style: { stroke: "#475569", strokeWidth: 1.5 },
          markerEnd: { type: MarkerType.ArrowClosed, color: "#475569" },
          animated: false,
        }));

        setRfNodes(flowNodes);
        setRfEdges(flowEdges);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Erro desconhecido");
      } finally {
        setLoading(false);
      }
    },
    [nodeIdInput, depth, navigate, setRfNodes, setRfEdges],
  );

  // ─── Clique em nó abre modal ──────────────────────────────────────────────
  const onNodeClick = useCallback(
    (_: React.MouseEvent, node: Node) => {
      const raw = rawNodesRef.current.find((n) => n.id === node.id);
      if (raw) setSelectedNode(raw);
    },
    [],
  );

  // ─── Render ───────────────────────────────────────────────────────────────
  return (
    <AppLayout title={t("impact.title")} subtitle={t("impact.subtitle")}>
      {/* Barra de busca */}
      <Card>
        <CardContent className="grid gap-3 p-4 sm:grid-cols-[minmax(0,1fr)_160px_auto] sm:items-end">
          <div>
            <label className="mb-1.5 block text-xs font-medium text-muted-foreground">
              ID do artefato (node_id)
            </label>
            <Input
              placeholder="Ex: story-abc123 ou uuid…"
              value={nodeIdInput}
              onChange={(e) => setNodeIdInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleSearch()}
            />
          </div>
          <div>
            <label className="mb-1.5 block text-xs font-medium text-muted-foreground">
              Profundidade
            </label>
            <Select value={depth} onValueChange={setDepth}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {[1, 2, 3, 4, 5, 7, 10].map((d) => (
                  <SelectItem key={d} value={String(d)}>
                    {d} {d === 1 ? "nível" : "níveis"}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <Button
            className="h-10 gap-2"
            onClick={() => handleSearch()}
            disabled={loading || !nodeIdInput.trim()}
          >
            {loading ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <Search className="h-4 w-4" />
            )}
            {loading ? "Analisando…" : "Analisar"}
          </Button>
        </CardContent>
      </Card>

      {/* Legenda de cores */}
      <div className="mt-3 flex flex-wrap gap-2">
        {Object.entries(NODE_COLORS).map(([label, color]) => (
          <Badge
            key={label}
            variant="outline"
            style={{ borderColor: color.border, color: color.border }}
            className="text-xs"
          >
            {label}
          </Badge>
        ))}
      </div>

      {/* Área do grafo */}
      <div className="mt-4 h-[560px] overflow-hidden rounded-xl border border-border bg-[#0f172a]">
        {!searched && !loading && (
          <div className="flex h-full flex-col items-center justify-center gap-3 text-muted-foreground">
            <Network className="h-10 w-10 opacity-30" />
            <p className="text-sm">Informe o ID de um artefato para visualizar o grafo de impacto</p>
          </div>
        )}

        {loading && (
          <div className="flex h-full items-center justify-center gap-3 text-muted-foreground">
            <Loader2 className="h-6 w-6 animate-spin" />
            <span className="text-sm">Carregando grafo…</span>
          </div>
        )}

        {!loading && error && (
          <div className="flex h-full flex-col items-center justify-center gap-3 px-8 text-center">
            <AlertCircle className="h-8 w-8 text-destructive" />
            <p className="text-sm text-destructive">{error}</p>
          </div>
        )}

        {!loading && !error && rfNodes.length > 0 && (
          <ReactFlow
            nodes={rfNodes}
            edges={rfEdges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            onNodeClick={onNodeClick}
            fitView
            fitViewOptions={{ padding: 0.2 }}
            minZoom={0.2}
            maxZoom={2}
            colorMode="dark"
          >
            <Background color="#1e293b" gap={20} />
            <Controls />
            <MiniMap
              nodeColor={(n) => {
                const raw = rawNodesRef.current.find((r) => r.id === n.id);
                return (NODE_COLORS[raw?.label ?? ""] ?? DEFAULT_COLOR).border;
              }}
              style={{ background: "#1e293b" }}
            />
            <Panel position="top-right" className="text-xs text-muted-foreground">
              {rfNodes.length} nós · {rfEdges.length} relações · clique num nó para detalhes
            </Panel>
          </ReactFlow>
        )}
      </div>

      {/* Modal de detalhes do nó */}
      <Dialog open={!!selectedNode} onOpenChange={(open) => !open && setSelectedNode(null)}>
        <DialogContent className="max-h-[80vh] overflow-y-auto sm:max-w-lg">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              {selectedNode && (
                <Badge
                  variant="outline"
                  style={{
                    borderColor: (NODE_COLORS[selectedNode.label] ?? DEFAULT_COLOR).border,
                    color: (NODE_COLORS[selectedNode.label] ?? DEFAULT_COLOR).border,
                  }}
                >
                  {selectedNode.label}
                </Badge>
              )}
              <span className="truncate text-sm font-semibold">
                {selectedNode
                  ? ((selectedNode.properties.title as string) ??
                    (selectedNode.properties.description as string)?.slice(0, 60) ??
                    selectedNode.id)
                  : ""}
              </span>
            </DialogTitle>
          </DialogHeader>

          {selectedNode && (
            <div className="mt-2 space-y-1">
              <p className="mb-3 font-mono text-xs text-muted-foreground">{selectedNode.id}</p>
              <table className="w-full text-sm">
                <tbody>
                  {Object.entries(selectedNode.properties).map(([key, value]) => (
                    <tr key={key} className="border-b border-border last:border-0">
                      <td className="py-2 pr-4 font-medium text-muted-foreground">{key}</td>
                      <td className="py-2 text-foreground">
                        {typeof value === "object"
                          ? JSON.stringify(value)
                          : String(value ?? "—")}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </AppLayout>
  );
}
