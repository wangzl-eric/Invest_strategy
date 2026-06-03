"""Unit tests for news service and news API routes."""

from unittest.mock import AsyncMock, MagicMock, patch

import pandas as pd
import pytest


class TestNewsService:
    """Test the NewsService class."""

    def test_news_service_init_without_client(self):
        """Test NewsService initialization without explicit client."""
        from backend.news_service import NewsService

        service = NewsService()
        assert service._ib_client is None

    def test_news_service_init_with_client(self, mock_ibkr_client):
        """Test NewsService initialization with provided client."""
        from backend.news_service import NewsService

        service = NewsService(ib_client=mock_ibkr_client)
        assert service._ib_client is mock_ibkr_client

    def test_ib_client_property_creates_client(self):
        """Test that ib_client property creates client if None."""
        from backend.news_service import NewsService

        with patch("backend.news_service.IBKRClient") as mock_client_class:
            mock_client_instance = Mock()
            mock_client_class.return_value = mock_client_instance

            service = NewsService()
            client = service.ib_client

            mock_client_class.assert_called_once()
            assert client is mock_client_instance

    def test_ib_client_property_returns_existing(self, mock_ibkr_client):
        """Test that ib_client property returns existing client."""
        from backend.news_service import NewsService

        service = NewsService(ib_client=mock_ibkr_client)
        assert service.ib_client is mock_ibkr_client

    @pytest.mark.asyncio
    async def test_get_equity_news(self, mock_ibkr_client, mock_news_articles):
        """Test getting equity news."""
        from backend.news_service import NewsService

        mock_ibkr_client.get_news_articles = AsyncMock(return_value=mock_news_articles)

        service = NewsService(ib_client=mock_ibkr_client)
        _ = await service.get_equity_news("AAPL", max_articles=5)

        mock_ibkr_client.get_news_articles.assert_called_once_with(
            symbol="AAPL",
            sec_type="STK",
            exchange="SMART",
            currency="USD",
            provider_code="IBKR",
            max_articles=5,
        )
        assert len(articles) == 3

    @pytest.mark.asyncio
    async def test_get_equity_news_df(self, mock_ibkr_client, mock_news_df):
        """Test getting equity news as DataFrame."""
        from backend.news_service import NewsService

        mock_ibkr_client.get_news_for_contract = AsyncMock(return_value=mock_news_df)

        service = NewsService(ib_client=mock_ibkr_client)
        df = await service.get_equity_news_df("AAPL", max_articles=5)

        mock_ibkr_client.get_news_for_contract.assert_called_once_with(
            symbol="AAPL",
            sec_type="STK",
            exchange="SMART",
            currency="USD",
        )
        assert isinstance(df, pd.DataFrame)
        assert "title" in df.columns

    @pytest.mark.asyncio
    async def test_get_forex_news(self, mock_ibkr_client, mock_forex_news_articles):
        """Test getting forex news."""
        from backend.news_service import NewsService

        mock_ibkr_client.get_news_articles = AsyncMock(
            return_value=mock_forex_news_articles
        )

        service = NewsService(ib_client=mock_ibkr_client)
        _ = await service.get_forex_news("EURUSD", max_articles=5)

        mock_ibkr_client.get_news_articles.assert_called_once()
        call_kwargs = mock_ibkr_client.get_news_articles.call_args.kwargs
        assert call_kwargs["symbol"] == "EURUSD"
        assert call_kwargs["sec_type"] == "CASH"
        assert call_kwargs["exchange"] == "IDEALPRO"

    @pytest.mark.asyncio
    async def test_get_futures_news(self, mock_ibkr_client, mock_news_articles):
        """Test getting futures news."""
        from backend.news_service import NewsService

        mock_ibkr_client.get_news_articles = AsyncMock(return_value=mock_news_articles)

        service = NewsService(ib_client=mock_ibkr_client)
        _ = await service.get_futures_news("ES", exchange="CME", max_articles=5)

        mock_ibkr_client.get_news_articles.assert_called_once()
        call_kwargs = mock_ibkr_client.get_news_articles.call_args.kwargs
        assert call_kwargs["symbol"] == "ES"
        assert call_kwargs["sec_type"] == "FUT"
        assert call_kwargs["exchange"] == "CME"

    @pytest.mark.asyncio
    async def test_get_index_news(self, mock_ibkr_client, mock_news_articles):
        """Test getting index news."""
        from backend.news_service import NewsService

        mock_ibkr_client.get_news_articles = AsyncMock(return_value=mock_news_articles)

        service = NewsService(ib_client=mock_ibkr_client)
        articles = await service.get_index_news("SPX", exchange="CME", max_articles=5)

        mock_ibkr_client.get_news_articles.assert_called_once()
        call_kwargs = mock_ibkr_client.get_news_articles.call_args.kwargs
        assert call_kwargs["symbol"] == "SPX"
        assert call_kwargs["sec_type"] == "IND"

    @pytest.mark.asyncio
    async def test_get_market_bulletins(self, mock_ibkr_client, mock_market_bulletins):
        """Test getting market bulletins."""
        from backend.news_service import NewsService

        mock_ibkr_client.get_market_bulletins = AsyncMock(
            return_value=mock_market_bulletins
        )

        service = NewsService(ib_client=mock_ibkr_client)
        bulletins = await service.get_market_bulletins(all_messages=True)

        mock_ibkr_client.get_market_bulletins.assert_called_once()
        # Check it was called (positional arg True)
        mock_ibkr_client.get_market_bulletins.assert_called_once_with(True)
        assert len(bulletins) == 2

    @pytest.mark.asyncio
    async def test_get_portfolio_news(self, mock_ibkr_client, mock_news_articles):
        """Test getting news for multiple symbols."""
        from backend.news_service import NewsService

        mock_ibkr_client.get_news_articles = AsyncMock(return_value=mock_news_articles)

        service = NewsService(ib_client=mock_ibkr_client)
        results = await service.get_portfolio_news(
            ["AAPL", "MSFT"], max_articles_per_symbol=2
        )

        assert "AAPL" in results
        assert "MSFT" in results
        assert mock_ibkr_client.get_news_articles.call_count == 2

    @pytest.mark.asyncio
    async def test_get_portfolio_news_handles_errors(self, mock_ibkr_client):
        """Test portfolio news handles individual symbol errors gracefully."""
        from backend.news_service import NewsService

        # First call succeeds, second call fails
        mock_ibkr_client.get_news_articles = AsyncMock(
            side_effect=[Exception("Network error"), []]
        )

        service = NewsService(ib_client=mock_ibkr_client)
        results = await service.get_portfolio_news(
            ["AAPL", "MSFT"], max_articles_per_symbol=2
        )

        # Should have entries for both symbols, failed one should be empty
        assert "AAPL" in results
        assert "MSFT" in results

    def test_get_available_providers(self):
        """Test getting available news providers."""
        from backend.news_service import NewsService

        service = NewsService()
        providers = service.get_available_providers()

        assert isinstance(providers, dict)
        assert "IBKR" in providers


class TestNewsProviders:
    """Test news provider constants."""

    def test_news_providers_defined(self):
        """Test that NEWS_PROVIDERS is defined."""
        from backend.ibkr_client import NEWS_PROVIDERS

        assert isinstance(NEWS_PROVIDERS, dict)
        assert "IBKR" in NEWS_PROVIDERS

    def test_ibkr_provider_description(self):
        """Test IBKR provider has a description."""
        from backend.ibkr_client import NEWS_PROVIDERS

        assert "IBKR" in NEWS_PROVIDERS
        assert isinstance(NEWS_PROVIDERS["IBKR"], str)
        assert len(NEWS_PROVIDERS["IBKR"]) > 0


class TestNewsRoutesRequestModels:
    """Test news API request/response models."""

    def test_equity_news_request_defaults(self):
        """Test EquityNewsRequest default values."""
        from backend.api.news_routes import EquityNewsRequest

        req = EquityNewsRequest(symbol="AAPL")
        assert req.symbol == "AAPL"
        assert req.max_articles == 10
        assert req.provider_code == "IBKR"

    def test_equity_news_request_custom(self):
        """Test EquityNewsRequest with custom values."""
        from backend.api.news_routes import EquityNewsRequest

        req = EquityNewsRequest(symbol="MSFT", max_articles=5, provider_code="DJ")
        assert req.symbol == "MSFT"
        assert req.max_articles == 5
        assert req.provider_code == "DJ"

    def test_forex_news_request(self):
        """Test ForexNewsRequest model."""
        from backend.api.news_routes import ForexNewsRequest

        req = ForexNewsRequest(pair="EURUSD", max_articles=20)
        assert req.pair == "EURUSD"
        assert req.max_articles == 20

    def test_futures_news_request(self):
        """Test FuturesNewsRequest model."""
        from backend.api.news_routes import FuturesNewsRequest

        req = FuturesNewsRequest(
            symbol="ES", exchange="CME", currency="USD", max_articles=15
        )
        assert req.symbol == "ES"
        assert req.exchange == "CME"
        assert req.currency == "USD"
        assert req.max_articles == 15

    def test_index_news_request(self):
        """Test IndexNewsRequest model."""
        from backend.api.news_routes import IndexNewsRequest

        req = IndexNewsRequest(symbol="SPX", exchange="CME", currency="USD")
        assert req.symbol == "SPX"
        assert req.exchange == "CME"

    def test_portfolio_news_request(self):
        """Test PortfolioNewsRequest model."""
        from backend.api.news_routes import PortfolioNewsRequest

        req = PortfolioNewsRequest(
            symbols=["AAPL", "MSFT", "GOOGL"],
            max_articles_per_symbol=5,
        )
        assert len(req.symbols) == 3
        assert "AAPL" in req.symbols
        assert req.max_articles_per_symbol == 5

    def test_news_response_model(self):
        """Test NewsResponse model."""
        from backend.api.news_routes import NewsResponse

        articles = [{"id": "1", "title": "Test"}]
        resp = NewsResponse(articles=articles, symbol="AAPL", count=1)
        assert len(resp.articles) == 1
        assert resp.symbol == "AAPL"
        assert resp.count == 1

    def test_bulletin_response_model(self):
        """Test BulletinResponse model."""
        from backend.api.news_routes import BulletinResponse

        bulletins = [{"msg_id": "1", "headline": "Test"}]
        resp = BulletinResponse(bulletins=bulletins, count=1)
        assert len(resp.bulletins) == 1
        assert resp.count == 1

    def test_providers_response_model(self):
        """Test ProvidersResponse model."""
        from backend.api.news_routes import ProvidersResponse

        providers = {"IBKR": "Free news from IBKR"}
        resp = ProvidersResponse(providers=providers)
        assert resp.providers == providers


class TestNewsRoutesEndpoints:
    """Test news API endpoints."""

    @pytest.mark.asyncio
    async def test_health_check(self):
        """Test news health check endpoint."""
        from backend.api.news_routes import news_health_check

        result = await news_health_check()

        assert result["status"] == "available"
        assert result["service"] == "IBKR News API"

    @pytest.mark.asyncio
    async def test_providers_endpoint(self):
        """Test providers endpoint."""
        from backend.api.news_routes import get_news_providers

        result = await get_news_providers()

        # Result is a ProvidersResponse pydantic model
        assert hasattr(result, "providers")
        assert "IBKR" in result.providers

    @pytest.mark.asyncio
    async def test_equity_news_endpoint(self):
        """Test equity news endpoint with mocked client."""
        from unittest.mock import AsyncMock, patch

        from backend.api.news_routes import EquityNewsRequest, get_equity_news

        mock_client = AsyncMock()
        mock_client.connect = AsyncMock(return_value=True)
        mock_client.disconnect = AsyncMock()
        mock_client.get_news_articles = AsyncMock(
            return_value=[
                {
                    "id": "1",
                    "title": "Test Article",
                    "source": "Reuters",
                    "timestamp": "2024-01-15T14:00:00",
                    "summary": "Test summary",
                    "url": "https://example.com",
                }
            ]
        )

        with patch("backend.api.news_routes.IBKRClient", return_value=mock_client):
            request = EquityNewsRequest(symbol="AAPL", max_articles=5)
            result = await get_equity_news(request)

            assert result.symbol == "AAPL"
            assert result.count == 1
            assert len(result.articles) == 1

    @pytest.mark.asyncio
    async def test_equity_news_df_endpoint(self):
        """Test equity news df endpoint with mocked client."""
        from unittest.mock import AsyncMock, patch

        from backend.api.news_routes import EquityNewsRequest, get_equity_news_df

        mock_client = AsyncMock()
        mock_client.connect = AsyncMock(return_value=True)
        mock_client.disconnect = AsyncMock()
        mock_client.get_news_for_contract = AsyncMock(
            return_value=pd.DataFrame(
                {
                    "date": pd.to_datetime(["2024-01-15"]),
                    "title": ["Test Article"],
                    "source": ["Reuters"],
                    "url": ["https://example.com"],
                }
            )
        )

        with patch("backend.api.news_routes.IBKRClient", return_value=mock_client):
            request = EquityNewsRequest(symbol="AAPL")
            result = await get_equity_news_df(request)

            assert result["symbol"] == "AAPL"
            assert result["count"] == 1

    @pytest.mark.asyncio
    async def test_forex_news_endpoint(self):
        """Test forex news endpoint with mocked client."""
        from unittest.mock import AsyncMock, patch

        from backend.api.news_routes import ForexNewsRequest, get_forex_news

        mock_client = AsyncMock()
        mock_client.connect = AsyncMock(return_value=True)
        mock_client.disconnect = AsyncMock()
        mock_client.get_news_articles = AsyncMock(return_value=[])

        with patch("backend.api.news_routes.IBKRClient", return_value=mock_client):
            request = ForexNewsRequest(pair="EURUSD", max_articles=10)
            result = await get_forex_news(request)

            assert result.symbol == "EURUSD"

    @pytest.mark.asyncio
    async def test_futures_news_endpoint(self):
        """Test futures news endpoint with mocked client."""
        from unittest.mock import AsyncMock, patch

        from backend.api.news_routes import FuturesNewsRequest, get_futures_news

        mock_client = AsyncMock()
        mock_client.connect = AsyncMock(return_value=True)
        mock_client.disconnect = AsyncMock()
        mock_client.get_news_articles = AsyncMock(return_value=[])

        with patch("backend.api.news_routes.IBKRClient", return_value=mock_client):
            request = FuturesNewsRequest(symbol="ES", exchange="CME")
            result = await get_futures_news(request)

            assert result.symbol == "ES"

    @pytest.mark.asyncio
    async def test_index_news_endpoint(self):
        """Test index news endpoint with mocked client."""
        from unittest.mock import AsyncMock, patch

        from backend.api.news_routes import IndexNewsRequest, get_index_news

        mock_client = AsyncMock()
        mock_client.connect = AsyncMock(return_value=True)
        mock_client.disconnect = AsyncMock()
        mock_client.get_news_articles = AsyncMock(return_value=[])

        with patch("backend.api.news_routes.IBKRClient", return_value=mock_client):
            request = IndexNewsRequest(symbol="SPX")
            result = await get_index_news(request)

            assert result.symbol == "SPX"

    @pytest.mark.asyncio
    async def test_market_bulletins_endpoint(self):
        """Test market bulletins endpoint with mocked client."""
        from unittest.mock import AsyncMock, patch

        from backend.api.news_routes import get_market_bulletins

        mock_client = AsyncMock()
        mock_client.connect = AsyncMock(return_value=True)
        mock_client.disconnect = AsyncMock()
        mock_client.get_market_bulletins = AsyncMock(
            return_value=[
                {
                    "msg_id": "1",
                    "timestamp": "2024-01-15T09:00:00",
                    "headline": "Test Bulletin",
                    "message": "Test message",
                    "exchange": "NYSE",
                }
            ]
        )

        with patch("backend.api.news_routes.IBKRClient", return_value=mock_client):
            result = await get_market_bulletins(all_messages=True)

            assert result.count == 1
            assert len(result.bulletins) == 1

    @pytest.mark.asyncio
    async def test_portfolio_news_endpoint(self):
        """Test portfolio news endpoint with mocked client."""
        from unittest.mock import AsyncMock, Mock, patch

        from backend.api.news_routes import PortfolioNewsRequest, get_portfolio_news

        # Create a mock IBKRClient
        mock_ib_client = AsyncMock()
        mock_ib_client.connect = AsyncMock(return_value=True)
        mock_ib_client.disconnect = AsyncMock()

        # Mock the news service
        mock_news_service = Mock()
        mock_news_service.get_portfolio_news = AsyncMock(
            return_value={
                "AAPL": [{"id": "1", "title": "AAPL News", "source": "Reuters"}],
                "MSFT": [{"id": "2", "title": "MSFT News", "source": "Bloomberg"}],
            }
        )

        with patch(
            "backend.api.news_routes.IBKRClient", return_value=mock_ib_client
        ), patch("backend.api.news_routes.NewsService", return_value=mock_news_service):
            request = PortfolioNewsRequest(
                symbols=["AAPL", "MSFT"], max_articles_per_symbol=3
            )
            result = await get_portfolio_news(request)

            assert "symbols" in result
            assert "news" in result
            assert "total_articles" in result


class TestNewsRoutesErrorHandling:
    """Test news API error handling."""

    @pytest.mark.asyncio
    async def test_equity_news_handles_connection_error(self):
        """Test equity news endpoint handles connection errors."""
        from unittest.mock import AsyncMock, patch

        from fastapi import HTTPException

        from backend.api.news_routes import EquityNewsRequest, get_equity_news

        mock_client = AsyncMock()
        mock_client.connect = AsyncMock(side_effect=Exception("Connection failed"))

        with patch("backend.api.news_routes.IBKRClient", return_value=mock_client):
            request = EquityNewsRequest(symbol="AAPL")
            with pytest.raises(HTTPException) as exc_info:
                await get_equity_news(request)
            assert exc_info.value.status_code == 500


class TestNewsServiceContextManager:
    """Test NewsService async context manager."""

    @pytest.mark.asyncio
    async def test_context_manager_enter_exit(self):
        """Test NewsService async context manager."""
        from backend.news_service import NewsService

        mock_client = AsyncMock()
        mock_client.connect = AsyncMock(return_value=True)
        mock_client.disconnect = AsyncMock()

        with patch("backend.news_service.IBKRClient", return_value=mock_client):
            async with NewsService() as service:
                assert service is not None

            mock_client.connect.assert_called_once()
            mock_client.disconnect.assert_called_once()


class TestNewsEdgeCases:
    """Test news service edge cases."""

    @pytest.mark.asyncio
    async def test_get_equity_news_empty_result(self):
        """Test getting equity news with no results."""
        from backend.news_service import NewsService

        mock_client = Mock()
        mock_client.get_news_articles = AsyncMock(return_value=[])

        service = NewsService(ib_client=mock_client)
        articles = await service.get_equity_news("INVALID")

        assert articles == []

    @pytest.mark.asyncio
    async def test_forex_news_pair_extraction(self):
        """Test forex pair currency extraction."""
        from backend.news_service import NewsService

        mock_client = Mock()
        mock_client.get_news_articles = AsyncMock(return_value=[])

        service = NewsService(ib_client=mock_client)
        await service.get_forex_news("EURUSD")

        call_kwargs = mock_client.get_news_articles.call_args.kwargs
        assert call_kwargs["currency"] == "USD"

    @pytest.mark.asyncio
    async def test_forex_news_short_pair(self):
        """Test forex news with short pair defaults to USD."""
        from backend.news_service import NewsService

        mock_client = Mock()
        mock_client.get_news_articles = AsyncMock(return_value=[])

        service = NewsService(ib_client=mock_client)
        await service.get_forex_news("EUR")

        call_kwargs = mock_client.get_news_articles.call_args.kwargs
        assert call_kwargs["currency"] == "USD"


# Mark all tests in this module as unit tests
pytestmark = pytest.mark.unit
