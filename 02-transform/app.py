import json
from pathlib import Path

from settings import settings
import transform
import pandas as pd


def deserialize_reports_raw(report_raw: Path) -> transform.ReportRaw:
    report_file_content = report_raw.read_text()
    report = json.loads(report_file_content)

    sprint_issues_report_file = transform.ReportRaw(**report)

    return sprint_issues_report_file


def persist_report_processed(report_processed_rows: list[transform.ReportProcessedRow], report_processed_path: Path):
    report_dict = [report_processed_row.dict() for report_processed_row in report_processed_rows]
    df = pd.DataFrame(report_dict)

    report_processed_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(report_processed_path, index=False)

    print(f"reports processed: {report_processed_path.absolute()}")


def join_reports_processed(reports_directory: Path):
    reports_processed_files = reports_directory.glob(f"*/report-processed.csv")

    output_path = Path(reports_directory, "issues.csv")

    dfs = [
        pd.read_csv(report_adapted)
        for report_adapted in sorted(reports_processed_files)
    ]

    data_frame = pd.concat(dfs)
    data_frame.to_csv(output_path, index=False)

    print(output_path)


def main():
    reports_directory = Path(settings["reports_directory"])
    report_raw_files = reports_directory.glob("*/report-raw.json")

    for report_raw_file in report_raw_files:
        report_raw = deserialize_reports_raw(report_raw_file)
        processed_report = transform.process_report(report_raw)

        report_processed_path = Path(reports_directory, report_raw.sprint, "report-processed.csv")
        persist_report_processed(processed_report, report_processed_path)

    join_reports_processed(reports_directory)


if __name__ == "__main__":
    main()
