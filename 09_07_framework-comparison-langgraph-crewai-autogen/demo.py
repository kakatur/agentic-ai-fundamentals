from framework_comparison import ProjectNeeds, rank_frameworks, recommendation


def main() -> None:
    needs = ProjectNeeds(control_flow=5, state_resume=5, operational_control=4)
    print(recommendation(needs))
    for name, points, notes in rank_frameworks(needs):
        print(f"{name}: {points} - {notes}")


if __name__ == "__main__":
    main()
