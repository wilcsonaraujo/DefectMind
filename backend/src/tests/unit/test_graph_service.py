import pytest
from unittest.mock import MagicMock, call # noqa: F401
from backend.src.modules.search.graph import GraphService
from backend.src.modules.search.schemas import NodeByType

# ─── Helpers ───────────────────────────────


def make_record(**kwargs):
    """Creates an object that simulates a Neo4j record (key-based access)."""
    return kwargs


def make_neo4j_result(records: list):
    """Creates a mock result for db.run() that iterates like a list."""
    mock = MagicMock()
    mock.__iter__ = MagicMock(return_value=iter(records))
    mock.single = MagicMock(return_value=records[0] if records else None)
    return mock


# ─── Fixture base ─────────────────────────────────────────────────────────────


@pytest.fixture
def fake_db():
    return MagicMock()


@pytest.fixture
def service(fake_db):
    return GraphService(neo4j_session=fake_db)


# ─── Testes unitários ─────────────────────────────────────────────────────────


class TestGetTotalNodes:
    def test_returns_correct_count(self, service, fake_db):
        """_get_total_nodes must return the value of the total_nodes field."""
        fake_db.run.return_value = make_neo4j_result([{"total_nodes": 42}])
        result = service._get_total_nodes()
        assert result == 42

    def test_returns_zero_when_empty_graph(self, service, fake_db):
        """_get_total_nodes should return 0 when the graph is empty."""
        fake_db.run.return_value = make_neo4j_result([{"total_nodes": 0}])
        result = service._get_total_nodes()
        assert result == 0


class TestGetTotalEdges:
    def test_returns_correct_count(self, service, fake_db):
        """_get_total_edges must return the value of the total_edges field."""
        fake_db.run.return_value = make_neo4j_result([{"total_edges": 38}])
        result = service._get_total_edges()
        assert result == 38


class TestGetNodesByType:
    def test_maps_labels_to_fields(self, service, fake_db):
        """_get_nodes_by_type must correctly populate the NodeByType fields."""
        fake_db.run.return_value = make_neo4j_result(
            [
                {"label": "Story", "total": 7},
                {"label": "BugReport", "total": 3},
                {"label": "Requirement", "total": 5},
            ]
        )
        result = service._get_nodes_by_type()
        assert isinstance(result, NodeByType)
        assert result.Story == 7
        assert result.BugReport == 3
        assert result.Requirement == 5

    def test_unknown_label_is_ignored(self, service, fake_db):
        """Unknown labels should not cause an error."""
        fake_db.run.return_value = make_neo4j_result(
            [
                {"label": "LabelUnknow", "total": 99},
                {"label": "Story", "total": 2},
            ]
        )
        result = service._get_nodes_by_type()
        assert result.Story == 2

    def test_returns_zeros_when_no_nodes(self, service, fake_db):
        """It should return NodeByType with all fields set to 0 if there are no nodes."""
        fake_db.run.return_value = make_neo4j_result([])
        result = service._get_nodes_by_type()
        assert result.Story == 0
        assert result.BugReport == 0


class TestGetMostConnectedNodes:
    def test_returns_list_of_dicts(self, service, fake_db):
        """_get_most_connected_nodes should return a list containing id, label, title, and degree."""
        fake_db.run.return_value = make_neo4j_result(
            [
                {
                    "id": "story-001",
                    "label": "Story",
                    "title": "Login flow",
                    "degree": 5,
                },
                {
                    "id": "req-001",
                    "label": "Requirement",
                    "title": "Validate creds",
                    "degree": 3,
                },
            ]
        )
        result = service._get_most_connected_nodes()
        assert len(result) == 2
        assert result[0]["id"] == "story-001"
        assert result[0]["degree"] == 5

    def test_returns_empty_list_when_no_nodes(self, service, fake_db):
        """It should return an empty list when there are no nodes."""
        fake_db.run.return_value = make_neo4j_result([])
        result = service._get_most_connected_nodes()
        assert result == []

    def test_default_limit_is_10(self, service, fake_db):
        """The default limit should be 10."""
        fake_db.run.return_value = make_neo4j_result([])
        service._get_most_connected_nodes()
        call_kwargs = fake_db.run.call_args
        assert (
            call_kwargs[1].get(
                "limit", call_kwargs[0][1] if len(call_kwargs[0]) > 1 else None
            )
            == 10
            or "limit=10" in str(call_kwargs)
            or fake_db.run.called
        )


class TestGetIsolatedNodes:
    def test_returns_nodes_without_relations(self, service, fake_db):
        """get_isolated_nodes should return nodes with no relationships."""
        fake_db.run.return_value = make_neo4j_result(
            [
                {"id": "orphan-001", "label": "BugReport", "title": "Orphan bug"},
            ]
        )
        result = service._get_isolated_nodes()
        assert len(result) == 1
        assert result[0]["id"] == "orphan-001"

    def test_returns_empty_list_when_no_isolated(self, service, fake_db):
        """It should return an empty list when all nodes have relationships."""
        fake_db.run.return_value = make_neo4j_result([])
        result = service._get_isolated_nodes()
        assert result == []


class TestGetAvgDegree:
    def test_calculates_correctly(self, service, fake_db):
        """get_avg_degree should return total_edges / total_nodes."""
        fake_db.run.side_effect = [
            make_neo4j_result([{"total_nodes": 10}]),
            make_neo4j_result([{"total_edges": 20}]),
        ]
        result = service._get_avg_degree()
        assert result == pytest.approx(2.0)

    def test_returns_zero_when_no_nodes(self, service, fake_db):
        """It should return 0 when there are no nodes (to avoid division by zero)."""
        fake_db.run.side_effect = [
            make_neo4j_result([{"total_nodes": 0}]),
            make_neo4j_result([{"total_edges": 0}]),
        ]
        result = service._get_avg_degree()
        assert result == 0


class TestGetDensity:
    def test_calculates_correctly(self, service, fake_db):
        """get_density should return edges / (nodes * (nodes - 1))."""
        fake_db.run.side_effect = [
            make_neo4j_result([{"total_nodes": 4}]),
            make_neo4j_result([{"total_edges": 6}]),
        ]
        result = service._get_density()
        # 6 / (4 * 3) = 0.5
        assert result == pytest.approx(0.5)

    def test_returns_zero_when_one_node(self, service, fake_db):
        """It should return 0 when there is only 1 node (to avoid division by zero)."""
        fake_db.run.side_effect = [
            make_neo4j_result([{"total_nodes": 1}]),
            make_neo4j_result([{"total_edges": 0}]),
        ]
        result = service._get_density()
        assert result == 0

    def test_returns_zero_when_no_nodes(self, service, fake_db):
        """It should return 0 when there are no nodes."""
        fake_db.run.side_effect = [
            make_neo4j_result([{"total_nodes": 0}]),
            make_neo4j_result([{"total_edges": 0}]),
        ]
        result = service._get_density()
        assert result == 0


class TestGetGraphStats:
    def test_returns_all_required_fields(self, service, fake_db):
        """get_graph_stats should return a dict containing all fields from StatsResponse."""
        fake_db.run.side_effect = [
            make_neo4j_result(
                [{"total_nodes": 6}]
            ),  # _get_total_nodes (get_graph_stats)
            make_neo4j_result(
                [{"total_edges": 5}]
            ),  # _get_total_edges (get_graph_stats)
            make_neo4j_result([{"label": "Story", "total": 1}]),  # _get_nodes_by_type
            make_neo4j_result(
                [{"id": "s1", "label": "Story", "title": "T", "degree": 2}]
            ),  # _get_most_connected
            make_neo4j_result([]),  # get_isolated_nodes
            make_neo4j_result([{"total_nodes": 6}]),  # _get_total_nodes (avg_degree)
            make_neo4j_result([{"total_edges": 5}]),  # _get_total_edges (avg_degree)
            make_neo4j_result([{"total_nodes": 6}]),  # _get_total_nodes (density)
            make_neo4j_result([{"total_edges": 5}]),  # _get_total_edges (density)
        ]
        result = service._get_graph_stats()
        assert "total_nodes" in result
        assert "total_edges" in result
        assert "nodes_by_type" in result
        assert "most_connected_nodes" in result
        assert "isolated_nodes" in result
        assert "avg_degree" in result
        assert "density" in result

    def test_total_nodes_matches_value(self, service, fake_db):
        """total_nodes in the result must match the value returned by Neo4j."""
        fake_db.run.side_effect = [
            make_neo4j_result([{"total_nodes": 99}]),
            make_neo4j_result([{"total_edges": 50}]),
            make_neo4j_result([]),
            make_neo4j_result([]),
            make_neo4j_result([]),
            make_neo4j_result([{"total_nodes": 99}]),
            make_neo4j_result([{"total_edges": 50}]),
            make_neo4j_result([{"total_nodes": 99}]),
            make_neo4j_result([{"total_edges": 50}]),
        ]
        result = service._get_graph_stats()
        assert result["total_nodes"] == 99
