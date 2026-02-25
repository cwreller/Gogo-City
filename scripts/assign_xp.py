"""
Assign XP to curated tasks using a formula based on existing fields.

XP Formula:
    xp = duration_xp + price_bonus + verification_bonus

Duration XP (scales with any range, 2 XP per minute of midpoint, min 50):
    20-30 min  -> midpoint 25  -> 50 XP
    30-45 min  -> midpoint 37  -> 74 XP
    45-60 min  -> midpoint 52  -> 104 XP (was 100 w/ old buckets)
    60-90 min  -> midpoint 75  -> 150 XP
    60-120 min -> midpoint 90  -> 180 XP (was 175 w/ old buckets)
    90-120 min -> midpoint 105 -> 210 XP

Price level bonus (higher cost = more commitment = more XP):
    1 -> +0 XP
    2 -> +15 XP
    3 -> +30 XP
    4 -> +50 XP

Verification type bonus (harder verification = more XP):
    gps   -> +0 XP   (just show up)
    photo -> +25 XP  (need to capture something specific)
    both  -> +50 XP  (GPS + photo proof)

Works with any city/duration range — no hardcoded buckets.
"""
import csv
import sys

PRICE_XP = {
    1: 0,
    2: 15,
    3: 30,
    4: 50,
}

VERIFICATION_XP = {
    "gps": 0,
    "photo": 25,
    "both": 50,
}


def duration_to_xp(duration_str: str) -> int:
    """Convert a duration range string to XP based on midpoint.
    
    Works with any range format: "20-30", "90-120", "45", etc.
    Formula: 2 XP per minute of midpoint, minimum 50.
    """
    if not duration_str or not duration_str.strip():
        return 75  # default for missing data
    
    duration_str = duration_str.strip()
    try:
        if "-" in duration_str:
            parts = duration_str.split("-")
            midpoint = (int(parts[0]) + int(parts[1])) / 2
        else:
            midpoint = float(duration_str)
    except (ValueError, IndexError):
        return 75
    
    return max(50, round(midpoint * 2))


def compute_xp(duration_str: str, price_level: int, verification_type: str) -> int:
    base = duration_to_xp(duration_str)
    price_bonus = PRICE_XP.get(price_level, 0)
    verify_bonus = VERIFICATION_XP.get(verification_type, 0)
    return base + price_bonus + verify_bonus


def main():
    input_path = "Gogo - nashville_template_tasks.csv"
    output_path = "Gogo - nashville_template_tasks.csv"

    if "--dry-run" in sys.argv:
        output_path = None

    with open(input_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        rows = list(reader)

    if "xp" not in fieldnames:
        fieldnames = list(fieldnames) + ["xp"]

    xp_distribution = {}
    for row in rows:
        duration = row.get("avg_duration_minutes", "").strip()
        price = int(row.get("price_level", 1) or 1)
        vtype = row.get("verification_type", "gps").strip()
        xp = compute_xp(duration, price, vtype)
        row["xp"] = xp

        bucket = f"{duration} / price {price} / {vtype}"
        xp_distribution.setdefault(xp, []).append(row["name"])

    print("=" * 60)
    print("XP FORMULA")
    print("=" * 60)
    print("  duration_xp + price_bonus + verification_bonus")
    print()
    print("  Duration:     2 XP per minute of midpoint (min 50)")
    print("                e.g. 20-30 -> 50 | 45-60 -> 104 | 60-90 -> 150 | 90-120 -> 210")
    print("  Price bonus:  1 -> +0 | 2 -> +15 | 3 -> +30 | 4 -> +50")
    print("  Verify bonus: gps -> +0 | photo -> +25 | both -> +50")
    print()
    print("=" * 60)
    print("XP ASSIGNMENTS")
    print("=" * 60)

    for row in rows:
        print(f"  {row['xp']:>3} XP  |  {row['name']}")

    print()
    print("=" * 60)
    print("DISTRIBUTION")
    print("=" * 60)
    for xp_val in sorted(xp_distribution.keys()):
        names = xp_distribution[xp_val]
        print(f"  {xp_val:>3} XP  ({len(names)} tasks)")

    total = sum(int(row["xp"]) for row in rows)
    avg = total / len(rows) if rows else 0
    print(f"\n  Total: {total} XP across {len(rows)} tasks")
    print(f"  Average: {avg:.0f} XP per task")
    print(f"  Range: {min(int(r['xp']) for r in rows)} - {max(int(r['xp']) for r in rows)} XP")

    if output_path:
        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        print(f"\n  Written to {output_path}")
    else:
        print("\n  (dry run - no file written)")


if __name__ == "__main__":
    main()
