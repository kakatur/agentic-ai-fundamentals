from context_compression import classify_line, compress_context, render_compressed_context


def test_classify_line_prioritizes_constraints():
    fact = classify_line("The response must not include secrets.")
    assert fact.kind == "constraint"
    assert fact.priority == 5


def test_compress_context_preserves_decisions_and_open_tasks():
    compressed = compress_context([
        "We decided to use batch imports.",
        "Next: write rollback plan.",
        "Background note one.",
        "Background note two.",
        "Background note three.",
    ])
    assert compressed.decisions == ("We decided to use batch imports.",)
    assert compressed.open_tasks == ("Next: write rollback plan.",)
    assert "Background note three" not in compressed.summary


def test_render_places_constraints_outside_summary():
    rendered = render_compressed_context(compress_context(["Never expose API keys.", "General note."]))
    assert "NON-NEGOTIABLE CONSTRAINTS" in rendered
    assert rendered.index("Never expose API keys") < rendered.index("SUMMARY")
