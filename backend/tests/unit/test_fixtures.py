def test_shared_fixtures_inject_deterministic_dependencies(
    api_client,
    mock_llm_client,
    mock_weather_service,
    request_id,
):
    response = api_client.get("/api/health")

    assert response.status_code == 200
    assert response.headers["X-Request-ID"] == request_id
    assert mock_llm_client.model_used == "mock-model"
    assert mock_weather_service.scenario == "rain"
