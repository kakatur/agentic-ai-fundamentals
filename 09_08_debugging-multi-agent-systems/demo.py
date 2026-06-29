from debugging_agents import analyze_trace, sample_bad_trace


def main() -> None:
    for finding in analyze_trace(sample_bad_trace()):
        print(f"{finding.severity}: {finding.code} - {finding.detail}")


if __name__ == "__main__":
    main()
