import math
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/calculate", methods=["POST"])
def calculate():
    """
    Uses the same logic as attendance.py:
      - Subtracts no-attendance classes from total to get effective_total
      - Calculates percentage from attended / effective_total
      - Bunkable / needed maths use effective_total
    """
    data = request.get_json()

    try:
        total_lectures = int(data.get("total", 0))
        attended_lectures = int(data.get("attended", 0))
        no_attendance_classes = int(data.get("no_attendance", 0))
        required = float(data.get("required", 75))
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid input. Please enter valid numbers."}), 400

    # ── validation ──
    if total_lectures <= 0:
        return jsonify({"error": "Total lectures must be greater than zero."}), 400
    if attended_lectures < 0:
        return jsonify({"error": "Attended lectures cannot be negative."}), 400
    if no_attendance_classes < 0:
        return jsonify({"error": "No-attendance classes cannot be negative."}), 400
    if not (1 <= required <= 100):
        return jsonify({"error": "Required percentage must be between 1 and 100."}), 400

    # ── effective total (mirrors attendance.py) ──
    effective_total = total_lectures - no_attendance_classes

    if effective_total <= 0:
        return jsonify({"error": "No valid lectures to calculate attendance."}), 400
    if attended_lectures > effective_total:
        return jsonify({"error": "Attended lectures cannot exceed effective total lectures."}), 400

    # ── core calculation ──
    percentage = (attended_lectures / effective_total) * 100
    required_fraction = required / 100

    result = {
        "percentage": round(percentage, 2),
        "total": total_lectures,
        "effective_total": effective_total,
        "attended": attended_lectures,
        "no_attendance": no_attendance_classes,
        "required": required,
    }

    if percentage >= required:
        # ✅ Eligible — how many lectures can be bunked
        # attended / (effective_total + x) >= required_fraction
        max_bunk = math.floor((attended_lectures / required_fraction) - effective_total)
        max_bunk = max(max_bunk, 0)

        result["eligible"] = True
        result["bunkable"] = max_bunk
        if max_bunk > 0:
            result["message"] = (
                f"You can safely skip up to {max_bunk} more lecture{'s' if max_bunk != 1 else ''} "
                f"and still stay above {required}%."
            )
        else:
            result["message"] = "You're right at the boundary — don't skip any more classes!"
    else:
        # ❌ Not eligible — how many lectures needed consecutively
        # (attended + x) / (effective_total + x) >= required_fraction
        if required_fraction >= 1:
            result["eligible"] = False
            result["needed"] = -1
            result["message"] = "100% required — impossible to recover by attending more."
        else:
            extra_lectures = math.ceil(
                (required_fraction * effective_total - attended_lectures)
                / (1 - required_fraction)
            )
            extra_lectures = max(extra_lectures, 0)
            result["eligible"] = False
            result["needed"] = extra_lectures
            result["message"] = (
                f"You must attend {extra_lectures} more lecture{'s' if extra_lectures != 1 else ''} "
                f"continuously to reach {required}%."
            )

    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True)
