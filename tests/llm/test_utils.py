from src.llm.utils import strip_markdown_code_fence


class TestStripMarkdownCodeFence:
    def test_plain_json_passes_through_unchanged(self):
        raw = '{"a": 1}'

        assert strip_markdown_code_fence(raw) == raw

    def test_strips_fenced_json_with_language_tag(self):
        raw = '```json\n{"a": 1}\n```'

        assert strip_markdown_code_fence(raw) == '{"a": 1}'

    def test_strips_fenced_json_without_language_tag(self):
        raw = '```\n{"a": 1}\n```'

        assert strip_markdown_code_fence(raw) == '{"a": 1}'

    def test_trims_surrounding_whitespace(self):
        raw = '  \n {"a": 1} \n  '

        assert strip_markdown_code_fence(raw) == '{"a": 1}'
