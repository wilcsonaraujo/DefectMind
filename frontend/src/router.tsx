import { QueryClient } from "@tanstack/react-query";
import { createRouter } from "@tanstack/react-router";
import { routeTree } from "./routeTree.gen";

export const getRouter = () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        // Sem isso, o default do react-query é staleTime: 0 — toda
        // remontagem (ex.: trocar de rota e voltar) refaz o fetch.
        // 30s é suficiente pra evitar refetch redundante em navegação
        // normal sem deixar os dados velhos por muito tempo.
        staleTime: 30_000,
      },
    },
  });

  const router = createRouter({
    routeTree,
    context: { queryClient },
    scrollRestoration: true,
    defaultPreloadStaleTime: 0,
  });

  return router;
};
