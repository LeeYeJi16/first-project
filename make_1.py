import pandas as pd
import json
from pathlib import Path


# =========================
# 설정값
# =========================

csv_file = "input.csv"
output_html = "output.html"

# HTML에서 필터로 사용할 컬럼명
filter_columns = [
    "분류 유형",
    "제품군",
    "문의 유형"
]

# 테이블에 보여줄 컬럼명
# 전체 컬럼을 보여주고 싶으면 None
display_columns = None
# 예시:
# display_columns = ["sessionid", "분류 유형", "제품군", "문의 유형", "질문", "답변"]


# =========================
# CSV 불러오기
# =========================

df = pd.read_csv(csv_file, encoding="utf-8-sig")

# 결측치 처리
df = df.fillna("")

# 표시 컬럼 설정
if display_columns is not None:
    df = df[display_columns]

# 필터 컬럼이 실제 CSV에 있는지 확인
missing_cols = [col for col in filter_columns if col not in df.columns]
if missing_cols:
    raise ValueError(f"CSV에 없는 필터 컬럼입니다: {missing_cols}")

# 데이터를 JSON 형태로 변환
data_json = df.to_dict(orient="records")
columns_json = list(df.columns)

# 필터 옵션 생성
filter_options = {
    col: sorted(df[col].astype(str).unique().tolist())
    for col in filter_columns
}


# =========================
# HTML 생성
# =========================

html = f"""
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <title>CSV 필터링 대시보드</title>

    <style>
        * {{
            box-sizing: border-box;
        }}

        body {{
            margin: 0;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
            background: #f4f6f8;
            color: #222;
        }}

        header {{
            background: linear-gradient(135deg, #1f2937, #374151);
            color: white;
            padding: 28px 40px;
        }}

        header h1 {{
            margin: 0;
            font-size: 28px;
            font-weight: 700;
        }}

        header p {{
            margin: 8px 0 0;
            color: #d1d5db;
            font-size: 14px;
        }}

        .container {{
            display: grid;
            grid-template-columns: 280px 1fr;
            gap: 24px;
            padding: 24px 40px;
        }}

        .sidebar {{
            background: white;
            border-radius: 16px;
            padding: 20px;
            box-shadow: 0 8px 20px rgba(0, 0, 0, 0.06);
            height: fit-content;
            position: sticky;
            top: 24px;
        }}

        .sidebar h2 {{
            font-size: 18px;
            margin: 0 0 16px;
        }}

        .filter-group {{
            border-top: 1px solid #e5e7eb;
            padding-top: 16px;
            margin-top: 16px;
        }}

        .filter-group h3 {{
            font-size: 14px;
            margin: 0 0 10px;
            color: #374151;
        }}

        .checkbox-list {{
            max-height: 180px;
            overflow-y: auto;
            padding-right: 4px;
        }}

        label {{
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 13px;
            margin-bottom: 8px;
            cursor: pointer;
            color: #374151;
        }}

        input[type="checkbox"] {{
            accent-color: #2563eb;
        }}

        .main {{
            min-width: 0;
        }}

        .toolbar {{
            background: white;
            border-radius: 16px;
            padding: 18px 20px;
            margin-bottom: 18px;
            box-shadow: 0 8px 20px rgba(0, 0, 0, 0.06);
            display: flex;
            gap: 12px;
            align-items: center;
            justify-content: space-between;
        }}

        .search-box {{
            flex: 1;
        }}

        .search-box input {{
            width: 100%;
            padding: 12px 14px;
            border: 1px solid #d1d5db;
            border-radius: 10px;
            font-size: 14px;
        }}

        .count-box {{
            white-space: nowrap;
            font-size: 14px;
            color: #4b5563;
            font-weight: 600;
        }}

        .reset-btn {{
            border: none;
            background: #ef4444;
            color: white;
            padding: 10px 14px;
            border-radius: 10px;
            cursor: pointer;
            font-weight: 600;
        }}

        .reset-btn:hover {{
            background: #dc2626;
        }}

        .table-card {{
            background: white;
            border-radius: 16px;
            overflow: hidden;
            box-shadow: 0 8px 20px rgba(0, 0, 0, 0.06);
        }}

        .table-wrapper {{
            overflow-x: auto;
            max-height: 720px;
            overflow-y: auto;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 13px;
        }}

        thead {{
            background: #f9fafb;
            position: sticky;
            top: 0;
            z-index: 1;
        }}

        th {{
            text-align: left;
            padding: 14px 12px;
            border-bottom: 1px solid #e5e7eb;
            color: #374151;
            font-weight: 700;
            white-space: nowrap;
        }}

        td {{
            padding: 12px;
            border-bottom: 1px solid #f1f5f9;
            vertical-align: top;
            max-width: 360px;
            line-height: 1.5;
        }}

        tr:hover {{
            background: #f8fafc;
        }}

        .badge {{
            display: inline-block;
            padding: 4px 8px;
            border-radius: 999px;
            font-size: 12px;
            font-weight: 700;
            background: #e5e7eb;
            color: #374151;
        }}

        .badge.negative {{
            background: #fee2e2;
            color: #b91c1c;
        }}

        .badge.positive {{
            background: #dcfce7;
            color: #166534;
        }}

        .badge.neutral {{
            background: #e0f2fe;
            color: #075985;
        }}

        .empty {{
            text-align: center;
            padding: 40px;
            color: #6b7280;
            font-size: 15px;
        }}

        @media (max-width: 900px) {{
            .container {{
                grid-template-columns: 1fr;
                padding: 20px;
            }}

            .sidebar {{
                position: static;
            }}

            .toolbar {{
                flex-direction: column;
                align-items: stretch;
            }}

            .count-box {{
                text-align: right;
            }}
        }}
    </style>
</head>

<body>

<header>
    <h1>CSV 필터링 대시보드</h1>
    <p>CSV 데이터를 조건별로 필터링하고 검색할 수 있는 HTML 페이지입니다.</p>
</header>

<div class="container">

    <aside class="sidebar">
        <h2>필터</h2>
        <div id="filters"></div>
    </aside>

    <main class="main">
        <div class="toolbar">
            <div class="search-box">
                <input 
                    type="text" 
                    id="searchInput" 
                    placeholder="전체 데이터에서 검색..."
                    oninput="applyFilters()"
                >
            </div>

            <div class="count-box">
                결과: <span id="resultCount">0</span>건
            </div>

            <button class="reset-btn" onclick="resetFilters()">초기화</button>
        </div>

        <div class="table-card">
            <div class="table-wrapper">
                <table>
                    <thead id="tableHead"></thead>
                    <tbody id="tableBody"></tbody>
                </table>
            </div>
        </div>
    </main>

</div>

<script>
    const rawData = {json.dumps(data_json, ensure_ascii=False)};
    const columns = {json.dumps(columns_json, ensure_ascii=False)};
    const filterColumns = {json.dumps(filter_columns, ensure_ascii=False)};
    const filterOptions = {json.dumps(filter_options, ensure_ascii=False)};

    let filteredData = [...rawData];

    function createFilters() {{
        const filtersDiv = document.getElementById("filters");
        filtersDiv.innerHTML = "";

        filterColumns.forEach(column => {{
            const group = document.createElement("div");
            group.className = "filter-group";

            const title = document.createElement("h3");
            title.textContent = column;
            group.appendChild(title);

            const list = document.createElement("div");
            list.className = "checkbox-list";

            filterOptions[column].forEach(value => {{
                const label = document.createElement("label");

                const checkbox = document.createElement("input");
                checkbox.type = "checkbox";
                checkbox.value = value;
                checkbox.dataset.column = column;
                checkbox.onchange = applyFilters;

                const span = document.createElement("span");
                span.textContent = value === "" ? "(빈 값)" : value;

                label.appendChild(checkbox);
                label.appendChild(span);
                list.appendChild(label);
            }});

            group.appendChild(list);
            filtersDiv.appendChild(group);
        }});
    }}

    function getSelectedFilters() {{
        const selected = {{}};

        filterColumns.forEach(column => {{
            selected[column] = [];
        }});

        document.querySelectorAll("input[type='checkbox']:checked").forEach(cb => {{
            selected[cb.dataset.column].push(cb.value);
        }});

        return selected;
    }}

    function applyFilters() {{
        const selected = getSelectedFilters();
        const searchText = document.getElementById("searchInput").value.toLowerCase().trim();

        filteredData = rawData.filter(row => {{
            const filterMatched = filterColumns.every(column => {{
                const selectedValues = selected[column];

                if (selectedValues.length === 0) {{
                    return true;
                }}

                return selectedValues.includes(String(row[column]));
            }});

            const searchMatched = searchText === "" || columns.some(column => {{
                return String(row[column]).toLowerCase().includes(searchText);
            }});

            return filterMatched && searchMatched;
        }});

        renderTable(filteredData);
    }}

    function renderTable(data) {{
        const tableHead = document.getElementById("tableHead");
        const tableBody = document.getElementById("tableBody");
        const resultCount = document.getElementById("resultCount");

        resultCount.textContent = data.length;

        tableHead.innerHTML = "";
        tableBody.innerHTML = "";

        const headerRow = document.createElement("tr");

        columns.forEach(column => {{
            const th = document.createElement("th");
            th.textContent = column;
            headerRow.appendChild(th);
        }});

        tableHead.appendChild(headerRow);

        if (data.length === 0) {{
            const tr = document.createElement("tr");
            const td = document.createElement("td");
            td.colSpan = columns.length;
            td.className = "empty";
            td.textContent = "조건에 맞는 데이터가 없습니다.";
            tr.appendChild(td);
            tableBody.appendChild(tr);
            return;
        }}

        data.forEach(row => {{
            const tr = document.createElement("tr");

            columns.forEach(column => {{
                const td = document.createElement("td");
                const value = row[column];

                if (column === "분류 유형") {{
                    const badge = document.createElement("span");
                    badge.className = "badge " + String(value).toLowerCase();
                    badge.textContent = value;
                    td.appendChild(badge);
                }} else {{
                    td.textContent = value;
                }}

                tr.appendChild(td);
            }});

            tableBody.appendChild(tr);
        }});
    }}

    function resetFilters() {{
        document.querySelectorAll("input[type='checkbox']").forEach(cb => {{
            cb.checked = false;
        }});

        document.getElementById("searchInput").value = "";
        filteredData = [...rawData];

        renderTable(filteredData);
    }}

    createFilters();
    renderTable(rawData);
</script>

</body>
</html>
"""


# =========================
# HTML 파일 저장
# =========================

Path(output_html).write_text(html, encoding="utf-8")

print(f"HTML 파일 생성 완료: {output_html}")