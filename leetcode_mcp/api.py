import logging
import re
import time
import json
import requests
from bs4 import BeautifulSoup
from typing import Dict, Any, Tuple, List, Optional

logger = logging.getLogger(__name__)


class LeetCodeAPI:
    def __init__(self, leetcode_session: str, csrftoken: str):
        if not leetcode_session or not csrftoken:
            raise ValueError("LEETCODE_SESSION and LEETCODE_CSRFTOKEN must be set.")
        self.leetcode_session = leetcode_session
        self.csrftoken = csrftoken
        self.base_url = "https://leetcode.com"
        self.graphql_url = f"{self.base_url}/graphql/"

    def _get_headers(self) -> Dict[str, str]:
        return {
            'Content-Type': 'application/json',
            'Cookie': f'LEETCODE_SESSION={self.leetcode_session}; csrftoken={self.csrftoken}',
            'x-csrftoken': self.csrftoken,
            'Origin': self.base_url,
        }

    def _make_request(self, url: str, method: str = 'POST', headers: Dict[str, str] = None, data: str = None) -> Dict[str, Any]:
        headers = headers or self._get_headers()
        try:
            response = requests.request(method, url, headers=headers, data=data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error making request to {url}: {e}")
            raise

    def fetch_problem_plain_text(self, link: str) -> Tuple[str, str]:
        match = re.search(r'/problems/([^/]+)/', link)
        if not match:
            raise ValueError("Invalid LeetCode problem URL")
        slug = match.group(1)

        payload = json.dumps({
            "query": """
                query questionContent($titleSlug: String!) {
                  question(titleSlug: $titleSlug) {
                    content
                    mysqlSchemas
                  }
                }
            """,
            "variables": {"titleSlug": slug}
        })

        response_json = self._make_request(self.graphql_url, data=payload)
        html_content = response_json.get('data', {}).get('question', {}).get('content', '')
        if not html_content:
            return "", slug

        soup = BeautifulSoup(html_content, "html.parser")
        return soup.get_text(), slug

    def generate_template(self, problem_slug: str, code_lang: str) -> str:
        payload = json.dumps({
            "query": """
                query questionEditorData($titleSlug: String!) {
                  question(titleSlug: $titleSlug) {
                    codeSnippets {
                      lang
                      langSlug
                      code
                    }
                  }
                }
            """,
            "variables": {"titleSlug": problem_slug}
        })

        data = self._make_request(self.graphql_url, data=payload)
        code_snippets = data.get('data', {}).get('question', {}).get('codeSnippets', [])
        matched_snippet = next((s for s in code_snippets if s['langSlug'] == code_lang), None)

        if matched_snippet:
            return matched_snippet['code']
        return f"No code found for language: {code_lang}"

    def _get_question_id(self, problem_slug: str) -> str:
        payload = json.dumps({
            "query": '''
                query consolePanelConfig($titleSlug: String!) {
                  question(titleSlug: $titleSlug) {
                    questionId
                  }
                }
            ''',
            "variables": {"titleSlug": problem_slug}
        })
        data = self._make_request(self.graphql_url, data=payload)
        question_data = data.get('data', {}).get('question')
        if not question_data or 'questionId' not in question_data:
            raise KeyError("'questionId' not found in response data.")
        return question_data['questionId']

    def _get_example_test_cases(self, problem_slug: str) -> List[str]:
        payload = json.dumps({
            "query": '''
                query consolePanelConfig($titleSlug: String!) {
                  question(titleSlug: $titleSlug) {
                    exampleTestcaseList
                  }
                }
            ''',
            "variables": {"titleSlug": problem_slug}
        })
        data = self._make_request(self.graphql_url, data=payload)
        question_data = data.get('data', {}).get('question')
        if not question_data or 'exampleTestcaseList' not in question_data:
            raise KeyError("'exampleTestcaseList' not found in response data.")
        return question_data['exampleTestcaseList']

    def _poll_for_result(self, check_url: str, headers: Dict[str, str]) -> Dict[str, Any]:
        for _ in range(15):  # Poll for 30 seconds max
            time.sleep(2)
            result = self._make_request(check_url, method='GET', headers=headers)
            if result.get("state") == "SUCCESS":
                return result
        return {"error": "Timed out waiting for LeetCode to process the request."}

    def run_code(self, problem_slug: str, code_lang: str, code: str) -> Dict[str, Any]:
        question_id = self._get_question_id(problem_slug)
        url = f"{self.base_url}/problems/{problem_slug}/interpret_solution/"
        test_cases = self._get_example_test_cases(problem_slug)

        payload = json.dumps({
            "lang": code_lang,
            "question_id": question_id,
            "typed_code": code,
            "data_input": "\n".join(test_cases)
        })

        headers = self._get_headers()
        headers['Referer'] = f"{self.base_url}/problems/{problem_slug}/"
        
        response_json = self._make_request(url, headers=headers, data=payload)
        interpret_id = response_json.get('interpret_id')
        if not interpret_id:
            return {"error": "Failed to get interpretation ID"}

        check_url = f"{self.base_url}/submissions/detail/{interpret_id}/check/"
        return self._poll_for_result(check_url, headers)

    def submit_code(self, problem_slug: str, code_lang: str, code: str) -> Dict[str, Any]:
        question_id = self._get_question_id(problem_slug)
        url = f"{self.base_url}/problems/{problem_slug}/submit/"

        payload = json.dumps({
            "lang": code_lang,
            "question_id": question_id,
            "typed_code": code
        })

        headers = self._get_headers()
        headers['Referer'] = f"{self.base_url}/problems/{problem_slug}/"

        response_json = self._make_request(url, headers=headers, data=payload)
        submission_id = response_json.get('submission_id')
        if not submission_id:
            return {"error": "Failed to get submission ID"}

        check_url = f"{self.base_url}/submissions/detail/{submission_id}/check/"
        return self._poll_for_result(check_url, headers)

    def fetch_daily_challenge(self) -> Dict[str, Any]:
        payload = json.dumps({
            "query": """
                query questionOfToday {
                  activeDailyCodingChallengeQuestion {
                    date
                    userStatus
                    link
                    question {
                      acRate
                      difficulty
                      freqBar
                      frontendQuestionId: questionFrontendId
                      isFavor
                      paidOnly: isPaidOnly
                      status
                      title
                      titleSlug
                      hasVideoSolution
                      hasSolution
                      topicTags {
                        name
                        id
                        slug
                      }
                    }
                  }
                }
            """
        })

        response_json = self._make_request(self.graphql_url, data=payload)
        return response_json.get('data', {}).get('activeDailyCodingChallengeQuestion', {})

    def fetch_problem_simplified(self, title_slug: str) -> Dict[str, Any]:
        payload = json.dumps({
            "query": """
                query questionData($titleSlug: String!) {
                  question(titleSlug: $titleSlug) {
                    questionId
                    questionFrontendId
                    title
                    titleSlug
                    content
                    difficulty
                    stats
                    exampleTestcases
                    content
                    companyTagStats
                    topicTags {
                      name
                      slug
                    }
                  }
                }
            """,
            "variables": {"titleSlug": title_slug}
        })

        response_json = self._make_request(self.graphql_url, data=payload)
        return response_json.get('data', {}).get('question', {})

    def search_problems(
        self,
        category: str = "all-code-essentials",
        tags: Optional[List[str]] = None,
        difficulty: Optional[str] = None,
        search_keywords: Optional[str] = None,
        limit: int = 10,
        offset: int = 0,
    ) -> Dict[str, Any]:
        filters = {}
        if tags:
            filters["tags"] = tags
        if difficulty:
            filters["difficulty"] = difficulty
        if search_keywords:
            filters["searchKeywords"] = search_keywords

        payload = json.dumps({
            "query": """
                query problemsetQuestionList($categorySlug: String, $limit: Int, $skip: Int, $filters: QuestionListFilterInput) {
                  problemsetQuestionList: questionList(
                    categorySlug: $categorySlug
                    limit: $limit
                    skip: $skip
                    filters: $filters
                  ) {
                    total: totalNum
                    questions: data {
                      acRate
                      difficulty
                      freqBar
                      frontendQuestionId: questionFrontendId
                      isFavor
                      paidOnly: isPaidOnly
                      status
                      title
                      titleSlug
                      topicTags {
                        name
                        id
                        slug
                      }
                      hasSolution
                      hasVideoSolution
                    }
                  }
                }
            """,
            "variables": {
                "categorySlug": category,
                "limit": limit,
                "skip": offset,
                "filters": filters,
            },
        })

        response_json = self._make_request(self.graphql_url, data=payload)
        return response_json.get("data", {}).get("problemsetQuestionList", {})
