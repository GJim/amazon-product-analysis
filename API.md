# Amazon Product Analysis API Documentation

This document describes the backend API endpoints available in the Amazon Product Analysis system.

## Base URL

All API endpoints are prefixed with `/api`.

## Authentication

Currently, the API does not require authentication.

## Content Type

All requests and responses use JSON format with Content-Type `application/json`.

## Endpoints

### API Information

#### `GET /api/`

Returns basic information about the API including available endpoints.

**Response:**

```json
{
  "name": "Amazon Product Analysis API",
  "version": "1.0.0",
  "endpoints": {
    "/api/analyze": "Submit a product URL for analysis",
    "/api/task/{task_id}": "Check the status of a submitted analysis task"
  }
}
```

### Product Analysis

#### `POST /api/analyze`

Submit an Amazon product URL for analysis. The analysis will be performed asynchronously.

**Request Body:**

```json
{
  "url": "https://www.amazon.com/Example-Product/dp/B0XXXXXXXX",
  "max_products": 5,
  "max_competitive": 3
}
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `url` | string | **Required**. The Amazon product URL to analyze |
| `max_products` | integer | **Optional**. Maximum number of main products to analyze (default: 1) |
| `max_competitive` | integer | **Optional**. Maximum number of competitive products to analyze per main product |

**Response:**

```json
{
  "task_id": "a1b2c3d4-e5f6-7890-abcd-1234567890ab",
  "status": "pending"
}
```

### Task Status

#### `GET /api/task/{task_id}`

Get the status of a previously submitted analysis task.

**Path Parameters:**

| Parameter | Description |
|-----------|-------------|
| `task_id` | Task ID returned from the `/api/analyze` endpoint |

**Response:**

When task is pending or running:

```json
{
  "task_id": "a1b2c3d4-e5f6-7890-abcd-1234567890ab",
  "status": "pending",
  "result": null
}
```

When task is completed successfully:

```json
{
  "task_id": "a1b2c3d4-e5f6-7890-abcd-1234567890ab",
  "status": "success",
  "result": {
    "task_uuid": "a1b2c3d4-e5f6-7890-abcd-1234567890ab",
    "main_product": {
      "title": "Example Product",
      "price": "$19.99",
      "description": "This is an example product description.",
      "main_image_url": "https://example.com/image.jpg"
    },
    "competitive_products": [
      {
        "title": "Competitive Product 1",
        "price": "$18.99",
        "description": "This is a competitive product."
      }
    ],
    "market_analysis": "Market analysis text...",
    "optimization_suggests": "Optimization suggestions text..."
  }
}
```

When task fails:

```json
{
  "task_id": "a1b2c3d4-e5f6-7890-abcd-1234567890ab",
  "status": "error",
  "result": {
    "error": "Error message describing what went wrong"
  }
}
```

## WebSocket Connection

In addition to the RESTful API, real-time updates are available through WebSocket connections.

### WebSocket URL

```
ws://{server_address}/ws/{task_id}
```

| Parameter | Description |
|-----------|-------------|
| `task_id` | Task ID returned from the `/api/analyze` endpoint |

### WebSocket Messages

The server will send status updates as JSON messages:

```json
{
  "type": "status_update",
  "data": {
    "status": "running",
    "progress": 50,
    "message": "Analyzing competitive products"
  }
}
```

When the task is complete, the server will send the full results:

```json
{
  "type": "task_complete",
  "data": {
    // Complete task results as in the GET /api/task/{task_id} response
  }
}
```

## Error Codes

| Status Code | Description |
|-------------|-------------|
| 200 | Request successful |
| 400 | Bad request - invalid input parameters |
| 404 | Resource not found |
| 500 | Server error |

## Rate Limiting

Currently, there are no rate limits implemented on the API. However, excessive requests may be throttled in the future.
