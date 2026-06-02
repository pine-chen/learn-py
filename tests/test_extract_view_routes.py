from app.services.extract_view_routes import extract_view_routes

def test_extract_view_routes() -> None:
    paths = [
        "src/views/order/index.vue",
        "src/views/user/index.vue",
        "src/views/order/detail/index.vue",
        "src/components/Button.vue",
    ]

    result = extract_view_routes(paths)

    assert result == [
        "/order",
        "/user",
        "/order/detail",
    ]