from extractor import extract_medication


TEXT = "The patient was prescribed Paracetamol 500 mg twice daily."


def main():
    total_runs = 50
    success_count = 0
    failure_count = 0
    crash_count = 0

    print("=" * 60)
    print("        50-RUN STRUCTURED EXTRACTION TEST")
    print("=" * 60)

    for run_number in range(1, total_runs + 1):

        print(f"\nRun {run_number}/{total_runs}")

        try:
            result = extract_medication(TEXT)

            if result is not None:
                success_count += 1
                print("Status: SUCCESS")
                print("Result:", result)

            else:
                failure_count += 1
                print("Status: CLEAN FAILURE")

        except Exception as error:
            crash_count += 1
            print("Status: CRASH")
            print("Error:", error)

    print("\n" + "=" * 60)
    print("                 FINAL RESULTS")
    print("=" * 60)

    print(f"Total runs       : {total_runs}")
    print(f"Successful       : {success_count}")
    print(f"Clean failures   : {failure_count}")
    print(f"Crashes          : {crash_count}")

    if crash_count == 0:
        print("\nPASS: Zero crashes across 50 runs.")
    else:
        print("\nFAIL: Crashes occurred.")


if __name__ == "__main__":
    main()