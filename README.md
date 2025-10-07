
# LeetCode MCP Server

[![Docker Pulls](https://img.shields.io/docker/pulls/ahm215/leetcode-mcp-server.svg)](https://hub.docker.com/r/ahm215/leetcode-mcp-server)
[![Build Status](https://img.shields.io/github/actions/workflow/status/AHM215/leetcode-mcp/ci.yml?branch=main)](https://github.com/AHM215/leetcode-mcp/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

An MCP-compatible server that exposes a set of tools to interact with the LeetCode API. This allows you to fetch problems, generate code templates, run, and submit solutions programmatically.

## Overview

This project provides a simple and effective way to interface with LeetCode's services. It's built using Python and the `mcp` framework, exposing functionalities as tools that can be easily integrated into other applications or used for automating LeetCode tasks.

## Features

- **Fetch Problem Details**: Get the full description, examples, and constraints for any LeetCode problem.
- **Code Template Generation**: Generate starter code for any problem in your preferred language.
- **Run Code**: Test your solution against the example test cases.
- **Submit Code**: Submit your solution for evaluation against the full test suite.
- **Daily Challenge**: Fetch the current daily LeetCode challenge.
- **Search Problems**: Search for problems with various filters like tags, difficulty, and keywords.

## Getting Started

### Prerequisites

- Python 3.12+
- Docker (for containerized deployment)
- Git

### Configuration

To interact with the LeetCode API, you need to provide your `LEETCODE_SESSION` and `LEETCODE_CSRFTOKEN` cookies.

1.  **Log in** to your LeetCode account in your web browser.
2.  **Open the developer tools** (usually by pressing `F12` or `Ctrl+Shift+I`).
3.  Go to the **Application** (or **Storage**) tab.
4.  Find the **Cookies** section and select `https://leetcode.com`.
5.  Locate the `LEETCODE_SESSION` and `csrftoken` cookies and copy their values.

Create a `.env` file in the root of the project and add your credentials:

```env
# .env
LEETCODE_SESSION=your_leetcode_session_cookie
LEETCODE_CSRFTOKEN=your_leetcode_csrftoken
```

### Local Installation

1.  **Clone the repository:**
    ```sh
    git clone https://github.com/AHM215/leetcode-mcp.git
    cd leetcode-mcp
    ```

2.  **Install dependencies:**
    ```sh
    pip install uv
    uv pip install -e .
    ```

3.  **Run the server:**
    ```sh
    mcp
    ```
    The server will start, and you can interact with it using an MCP client.

## Docker Usage

### Pull from Docker Hub

You can pull the pre-built Docker image from Docker Hub.

```sh
docker pull ahm215/leetcode-mcp-server:latest
```

### Run with Docker

To run the server using Docker, you need to pass your LeetCode credentials as environment variables.

```sh
docker run -d \
  -p 8000:8000 \
  --name leetcode-mcp-server \
  -e LEETCODE_SESSION="your_leetcode_session_cookie" \
  -e LEETCODE_CSRFTOKEN="your_leetcode_csrftoken" \
  ahm215/leetcode-mcp-server:latest
```

### Build from Source

You can also build the Docker image from the source code.

1.  **Clone the repository** (if you haven't already).
2.  **Build the image:**
    ```sh
    docker build -t leetcode-mcp-server .
    ```
3.  **Run the container** as shown in the "Run with Docker" section, using `leetcode-mcp-server` as the image name.

## Available Tools (API)

The server exposes the following tools:

---

### `fetch_problem_plain_text`

Fetches the plain text content of a LeetCode problem given its URL.

- **Parameters:**
  - `link` (str): The full URL of the LeetCode problem.
- **Returns:** (str) The plain text description of the problem.

---

### `generate_template`

Generates a language-specific code template for a given LeetCode problem.

- **Parameters:**
  - `problem_slug` (str): The slug of the problem from its URL (e.g., "two-sum").
  - `code_lang` (str): The language slug (e.g., "python3", "java", "cpp").
- **Returns:** (str) The code template.

---

### `run_code`

Executes code against the example test cases for a LeetCode problem.

- **Parameters:**
  - `problem_slug` (str): The slug of the problem.
  - `code_lang` (str): The language slug.
  - `code` (str): The code to be executed.
- **Returns:** (dict) The results of the execution.

---

### `submit_code`

Submits code for a LeetCode problem for evaluation against the full test suite.

- **Parameters:**
  - `problem_slug` (str): The slug of the problem.
  - `code_lang` (str): The language slug.
  - `code` (str): The code to be submitted.
- **Returns:** (dict) The submission result.

---

### `get_daily_challenge`

Retrieves today's LeetCode Daily Challenge problem.

- **Parameters:** None
- **Returns:** (dict) Details of the daily challenge problem.

---

### `get_problem`

Retrieves details about a specific LeetCode problem.

- **Parameters:**
  - `titleSlug` (str): The slug of the problem.
- **Returns:** (dict) Detailed information about the problem.

---

### `search_problems`

Searches for LeetCode problems based on various filters.

- **Parameters:**
  - `category` (str, optional): The category to search in. Defaults to "all-code-essentials".
  - `tags` (List[str], optional): A list of tags to filter by.
  - `difficulty` (str, optional): The difficulty level ("EASY", "MEDIUM", "HARD").
  - `searchKeywords` (str, optional): Keywords to search for.
  - `limit` (int, optional): The number of results to return. Defaults to 10.
  - `offset` (int, optional): The offset for pagination. Defaults to 0.
- **Returns:** (dict) A list of problems matching the criteria.

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue if you have any suggestions or find any bugs.

1.  Fork the repository.
2.  Create your feature branch (`git checkout -b feature/AmazingFeature`).
3.  Commit your changes (`git commit -m 'Add some AmazingFeature'`).
4.  Push to the branch (`git push origin feature/AmazingFeature`).
5.  Open a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
