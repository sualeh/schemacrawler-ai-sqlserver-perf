"""Tests for the Version MCP tool."""

import pytest
from unittest.mock import patch

from schemacrawler_ai_sqlserver_perf.tools.version_tool import version_tool, get_package_version


class TestVersionTool:
    """Test suite for version_tool."""

    @pytest.mark.asyncio
    async def test_version_basic_functionality(self):
        """Test basic version tool functionality."""
        result = await version_tool()

        assert isinstance(result, dict)
        assert result["success"] is True
        assert "SchemaCrawler" in result["message"]
        assert "version" in result["message"]

    @pytest.mark.asyncio
    async def test_version_return_structure(self):
        """Test that the return structure is correct."""
        result = await version_tool()

        required_keys = ["message", "server_name", "version", "timestamp", "tool", "success"]
        for key in required_keys:
            assert key in result

        assert result["tool"] == "version"
        assert isinstance(result["success"], bool)
        assert isinstance(result["message"], str)
        assert isinstance(result["server_name"], str)
        assert isinstance(result["version"], str)
        assert isinstance(result["timestamp"], str)

    @pytest.mark.asyncio
    async def test_version_includes_server_name_and_version(self):
        """Test that version tool includes both server name and version."""
        result = await version_tool()
        
        expected_server_name = "SchemaCrawler AI MCP Server for SQL Server Performance"
        assert result["server_name"] == expected_server_name
        assert expected_server_name in result["message"]
        assert result["version"] in result["message"]

    def test_get_package_version_fallback(self):
        """Test package version retrieval with fallback."""
        # Mock importlib.metadata.version to raise PackageNotFoundError
        with patch('schemacrawler_ai_sqlserver_perf.tools.version_tool.importlib.metadata.version') as mock_version:
            mock_version.side_effect = Exception("Package not found")
            
            # Mock pathlib and tomllib for fallback
            with patch('schemacrawler_ai_sqlserver_perf.tools.version_tool.pathlib.Path') as mock_path:
                mock_path_instance = mock_path.return_value.parent.parent.parent
                mock_pyproject = mock_path_instance / "pyproject.toml"
                mock_pyproject.exists.return_value = True
                
                with patch('schemacrawler_ai_sqlserver_perf.tools.version_tool.tomllib.load') as mock_tomllib:
                    mock_tomllib.return_value = {"project": {"version": "0.1.0"}}
                    
                    with patch('builtins.open'):
                        version = get_package_version()
                        assert version == "0.1.0"

    def test_get_package_version_unknown_fallback(self):
        """Test package version retrieval when all methods fail."""
        # Mock all methods to fail
        with patch('schemacrawler_ai_sqlserver_perf.tools.version_tool.importlib.metadata.version') as mock_version:
            mock_version.side_effect = Exception("Package not found")
            
            with patch('schemacrawler_ai_sqlserver_perf.tools.version_tool.pathlib.Path') as mock_path:
                mock_path_instance = mock_path.return_value.parent.parent.parent
                mock_pyproject = mock_path_instance / "pyproject.toml"
                mock_pyproject.exists.return_value = False
                
                version = get_package_version()
                assert version == "Unknown"
