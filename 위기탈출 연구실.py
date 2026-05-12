import tkinter as tk
from tkinter import messagebox
from collections import deque
import heapq
import random
import copy

# =====================================
# MAP 정의
# 0  벽
# 1  통로
# 2  출구
# string  방 이름 (D406 등)
# =====================================

grid = [
    [0,0,0,2,0,0,0,0,0,0,0,0],
    [0,0,2,1,0,0,0,0,2,0,0,0],
    ['D406','D406',1,1,'D407','D407','D408','D408',1,0,2,0],
    [1,1,1,1,1,1,1,1,1,1,1,2],
    ['D405','D405',2,1,'D404','D404','D403','D403','D402','D402','D401',0],
    [0,0,0,2,0,0,0,0,0,0,0,0]
]

ROWS = len(grid)
COLS = len(grid[0])
CELL_SIZE = 60

DIRS = [(-1,0),(1,0),(0,-1),(0,1)]

# =====================================
# 유틸 함수
# =====================================

def in_range(r, c)
    return 0 = r  ROWS and 0 = c  COLS

def manhattan(a, b)
    return abs(a[0]-b[0]) + abs(a[1]-b[1])

def neighbors(r, c)
    for dr, dc in DIRS
        nr, nc = r + dr, c + dc
        if in_range(nr, nc)
            yield nr, nc
            
def is_room(cell)
    return isinstance(cell, str)


# =====================================
# tkinter 설정
# =====================================

root = tk.Tk()
root.title(Forward Chaining Fire Evacuation)

canvas = tk.Canvas(
    root,
    width=COLS  CELL_SIZE,
    height=ROWS  CELL_SIZE,
    bg=white
)
canvas.pack(pady=10)

status_label = tk.Label(root, text=통로(흰색)를 클릭해서 사람 시작 위치를 선택하세요)
status_label.pack()

# =====================================
# 상태 변수
# =====================================

person = None
fires = []
fire_time = None
result_path = None
result_time = None


# =====================================
# 맵 그리기
# =====================================

def draw_map(person_pos=None, fire_positions=None, current_time=None, path=None)
    canvas.delete(all)
    visited_room = set()

    # =====================================
    # 1. 기본 맵 먼저 그리기
    # =====================================

    for r in range(ROWS)
        for c in range(COLS)
            x1 = c  CELL_SIZE
            y1 = r  CELL_SIZE
            x2 = x1 + CELL_SIZE
            y2 = y1 + CELL_SIZE

            value = grid[r][c]

            # =========================
            # 방
            # =========================

            if is_room(value)
                if (r, c) in visited_room
                    continue

                width_count = 1

                while (c + width_count  COLS and grid[r][c + width_count] == value)
                    visited_room.add((r, c + width_count))
                    width_count += 1

                merged_x2 = x1 + CELL_SIZE  width_count

                canvas.create_rectangle(
                    x1, y1,
                    merged_x2, y2,
                    fill=#FFD27F,
                    outline=gray
                )

                canvas.create_text(
                    (x1 + merged_x2)2,
                    (y1 + y2)2,
                    text=value,
                    font=(Arial, 10, bold)
                )

            # =========================
            # 통로  출구  벽
            # =========================

            else
                if value == 1
                    color = white

                elif value == 2
                    color = green

                else
                    color = black

                canvas.create_rectangle(
                    x1, y1, x2, y2,
                    fill=color,
                    outline=gray
                )

    # =====================================
    # 2. 사람이 지나간 경로
    # =====================================

    visited_path = set()
    if path
        for rr, cc in path

            # 출구 제외
            if grid[rr][cc]== 2 continue

            visited_path.add((rr, cc))

            x1 = cc  CELL_SIZE
            y1 = rr  CELL_SIZE
            x2 = x1 + CELL_SIZE
            y2 = y1 + CELL_SIZE

            canvas.create_rectangle(
                x1, y1, x2, y2,
                fill=light blue,
                outline=gray
            )

    # =====================================
    # 3. 연기 표시
    # =====================================

    if current_time is not None
        for r in range(ROWS)
            for c in range(COLS)
                if is_smoke(r, c, current_time)

                    x1 = c  CELL_SIZE
                    y1 = r  CELL_SIZE
                    x2 = x1 + CELL_SIZE
                    y2 = y1 + CELL_SIZE

                    # 사람이 지나간 경로면 연회색
                    if (r, c) in visited_path
                        smoke_color = #CFCFCF

                    else smoke_color = gray

                    canvas.create_rectangle(
                        x1, y1, x2, y2,
                        fill=smoke_color,
                        stipple=gray50,
                        outline=gray
                    )

    # =====================================
    # 4. 불 표시
    # =====================================

    if fire_positions
        for fr, fc in fire_positions

            x1 = fc  CELL_SIZE
            y1 = fr  CELL_SIZE
            x2 = x1 + CELL_SIZE
            y2 = y1 + CELL_SIZE

            # 사람이 지나간 경로면 연빨강
            if (fr, fc) in visited_path
                fire_color = #FF9999

            else fire_color = red

            canvas.create_rectangle(
                x1, y1, x2, y2,
                fill=fire_color,
                outline=black
            )

            canvas.create_text(
                (x1+x2)2,
                (y1+y2)2,
                text=F,
                font=(Arial, 18, bold),
                fill=white
            )

    # =====================================
    # 5. 현재 사람 위치
    # =====================================

    if person_pos
        pr, pc = person_pos

        x1 = pc  CELL_SIZE
        y1 = pr  CELL_SIZE
        x2 = x1 + CELL_SIZE
        y2 = y1 + CELL_SIZE

        canvas.create_oval(
            x1+10, y1+10,
            x2-10, y2-10,
            fill=blue
        )

        canvas.create_text(
            (x1+x2)2,
            (y1+y2)2,
            text=P,
            font=(Arial, 16, bold),
            fill=white
        )


# =====================================
# 불 시간 계산
# =====================================

def compute_fire_time()
    global fire_time
    
    INF = float('inf')

    fire_time = [[INF]COLS for _ in range(COLS)]

    q = deque()

    for fr, fc in fires
        fire_time[fr][fc] = 0
        q.append((fr, fc))

    while q
        r, c = q.popleft()
        
        for nr, nc in neighbors(r, c)
            if grid[nr][nc] != 0
                next_time = fire_time[r][c] + 3

                if fire_time[nr][nc]  next_time
                    fire_time[nr][nc] = next_time
                    q.append((nr, nc))


# =====================================
# 연기 판단
# =====================================

def is_smoke(r, c, t)
    # 벽에는 연기 없음
    if grid[r][c] == 0
        return False
    
    if fire_time is None
        return False

    for rr in range(ROWS)
        for cc in range(COLS)
            if fire_time[rr][cc] = t
                if manhattan((r,c), (rr,cc)) = 2
                    return True

    return False


# =====================================
# 안전 여부
# =====================================

def is_safe(r, c, t)
    if not in_range(r, c) return False
    if grid[r][c] == 0 return False
    if fire_time[r][c] = t return False
    if is_smoke(r, c, t) return False

    return True


# =====================================
# 탈출 경로 탐색
# =====================================

def escape()
    pq = []
    heapq.heappush(pq, (0, person, [person]))

    visited = set()

    while pq
        time, (r,c), path = heapq.heappop(pq)

        if (r,c,time) in visited continue

        visited.add((r,c,time))

        if grid[r][c] == 2 return time, path

        for nr, nc in neighbors(r, c)
            next_time = time + 1
            
            current_cell = grid[r][c]
            next_cell = grid[nr][nc]
            
            # =========================
            # 방 이동 규칙
            # =========================

            # 방 - 방 이동 금지
            if is_room(current_cell) and is_room(next_cell)
                continue

            # 방 - 통로 이동시 위아래만 가능
            if is_room(current_cell) and next_cell == 1
                # 좌우 이동 금지
                if nc != c continue
            
            if is_safe(nr, nc, next_time)
                heapq.heappush(
                    pq, (next_time,(nr, nc),path + [(nr, nc)])
                )

    return None


# =====================================
# 현재 시간 불 위치
# =====================================

def get_current_fire_positions(t)
    current_fires = []

    for r in range(ROWS)
        for c in range(COLS)
            if fire_time[r][c] = t
                current_fires.append((r,c))

    return current_fires


# =====================================
# 시뮬레이션 진행
# =====================================

def simulate(t=0)
    global result_path
    global result_time

    if t  result_time
        status_label.config(text=f대피 완료, 걸린시간 {result_time}초)
        return

    person_pos = result_path[t]
    current_fires = get_current_fire_positions(t)

    draw_map(
        person_pos=person_pos,
        fire_positions=current_fires,
        current_time=t,
        path=result_path[t+1]
    )

    status_label.config(
        text=f현재 시간  {t}초
    )

    root.after(1000, lambda simulate(t+1))


# =====================================
# 시작 함수
# =====================================

def start_simulation()
    global result_path
    global result_time

    compute_fire_time()

    result = escape()

    if result is None
        messagebox.showerror(실패, 탈출 가능한 경로가 없습니다)
        return

    result_time, result_path = result

    simulate(0)


# =====================================
# 사람 선택
# =====================================

def on_click(event)
    global person
    global fires

    c = event.x  CELL_SIZE
    r = event.y  CELL_SIZE

    if not in_range(r, c) return
    
    if grid[r][c] == 0 or grid[r][c] == 2
        messagebox.showwarning(경고,방 또는 통로만 선택 가능합니다)
        return

    person = (r, c)
                
    available_places = []
    for rr in range(ROWS)
        for cc in range(COLS)
            if grid[rr][cc] != 0 and grid[rr][cc] != 2
                available_places.append((rr, cc))

    possible_fire = [
        pos for pos in available_places
        if manhattan(pos, person)  2
    ]

    fire_count = random.randint(1, 3)

    fires = random.sample(
        possible_fire,
        min(fire_count, len(possible_fire))
    )

    draw_map(person_pos=person, fire_positions=fires)

    status_label.config(text=1초 후 시뮬레이션 시작)

    root.after(1000, start_simulation)


# =====================================
# 초기 화면
# =====================================

visited_room = set()
draw_map()

canvas.bind(Button-1, on_click)

root.mainloop()
