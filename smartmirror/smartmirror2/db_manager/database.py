import sqlite3
import json
import os

# 기존 main5.py 파일의 데이터를 복사하여 사용
BEAUTY_DATA = {
    '20': {
        'spring_warm': {
            'title': '20호 봄 웜톤 🌸', 'desc': "화사하고 생기 넘치는 당신! 인간 복숭아가 따로 없네요. 따뜻하고 밝은 코랄, 피치 컬러로 사랑스러움을 극대화해보세요.",
            'base' : {'지성': ['P001', 'P002'], '건성': ['P003', 'P004'], '복합성': ['P005', 'P006'], '민감성': ['P007', 'P008']},
            'color': {'eye': ['P009', 'P010'], 'lip': ['P011', 'P012', 'P013']}, 'makeup_styles': ['M001', 'M002', 'M003']
        },
        'summer_cool': {
            'title': '20호 여름 쿨톤 ☀️', 'desc': "맑고 투명한 당신! 핑크빛이 살짝 돌아 청순하고 깨끗한 이미지를 가졌네요. 라벤더, 라이트 핑크 등 파스텔 컬러가 잘 어울려요.",
            'base' : {'지성': ['P001', 'P002'], '건성': ['P003', 'P004'], '복합성': ['P005', 'P006'], '민감성': ['P007', 'P008']},
            'color': {'eye': ['P009', 'P010'], 'lip': ['P011', 'P012', 'P013']}, 'makeup_styles': ['M001', 'M002', 'M003']
        },
        'fall_warm': {
            'title': '20호 가을 웜톤 🍁',
            'desc': "깊고 분위기 있는 무드의 당신! 카멜, 올리브, 테라코타, 브릭 같은 따뜻하고 묵직한 컬러가 얼굴에 깊이를 더해줘요.",
            'base' : {'지성': ['P001', 'P002'], '건성': ['P003', 'P004'], '복합성': ['P005', 'P006'], '민감성': ['P007', 'P008']},
            'color': {'eye': ['P009', 'P010'], 'lip': ['P011', 'P012', 'P013']}, 'makeup_styles': ['M001', 'M002', 'M003']
        },
        'winter_cool': {
            'title': '20호 겨울 쿨톤 ❄️',
            'desc': "선명한 대비가 잘 어울리는 당신! 푸시아, 블루레드, 버건디, 딥 플럼처럼 차갑고 또렷한 컬러가 존재감을 살려줘요.",
            'base' : {'지성': ['P001', 'P002'], '건성': ['P003', 'P004'], '복합성': ['P005', 'P006'], '민감성': ['P007', 'P008']},
            'color': {'eye': ['P009', 'P010'], 'lip': ['P011', 'P012', 'P013']}, 'makeup_styles': ['M001', 'M002', 'M003']
        }
    },
    '21': {
        'spring_warm': {
            'title': '21호 봄 웜톤 🌸', 'desc': "화사하고 생기 있는 이미지의 당신! 코랄, 피치, 아이보리 등 따뜻하고 밝은 컬러로 매력을 발산해보세요.",
            'base' : {'지성': ['P001', 'P002'], '건성': ['P003', 'P004'], '복합성': ['P005', 'P006'], '민감성': ['P007', 'P008']},
            'color': {'eye': ['P009', 'P010'], 'lip': ['P011', 'P012', 'P013']}, 'makeup_styles': ['M001', 'M002', 'M003']
        },
        'summer_cool': {
            'title': '21호 여름 쿨톤 ☀️', 'desc': "맑고 깨끗한 이미지의 당신! 라벤더, 파스텔 핑크 등 부드럽고 시원한 컬러로 청초함을 뽐내보세요.",
            'base' : {'지성': ['P001', 'P002'], '건성': ['P003', 'P004'], '복합성': ['P005', 'P006'], '민감성': ['P007', 'P008']},
            'color': {'eye': ['P009', 'P010'], 'lip': ['P011', 'P012', 'P013']}, 'makeup_styles': ['M001', 'M002', 'M003']
        },
        'fall_warm': {
            'title': '21호 가을 웜톤 🍁',
            'desc': "부드럽고 고급스러운 무드의 당신! 카키, 카라멜, 코코아, 브릭 오렌지 등 저채도 웜 컬러가 피부를 건강하게 보여줘요.",
            'base' : {'지성': ['P001', 'P002'], '건성': ['P003', 'P004'], '복합성': ['P005', 'P006'], '민감성': ['P007', 'P008']},
            'color': {'eye': ['P009', 'P010'], 'lip': ['P011', 'P012', 'P013']}, 'makeup_styles': ['M001', 'M002', 'M003']
        },
        'winter_cool': {
            'title': '21호 겨울 쿨톤 ❄️',
            'desc': "도시적이고 시크한 당신! 쿨 로즈, 블루톤 레드, 베리, 블랙/네이비 계열이 또렷한 인상을 완성해줘요.",
            'base' : {'지성': ['P001', 'P002'], '건성': ['P003', 'P004'], '복합성': ['P005', 'P006'], '민감성': ['P007', 'P008']},
            'color': {'eye': ['P009', 'P010'], 'lip': ['P011', 'P012', 'P013']}, 'makeup_styles': ['M001', 'M002', 'M003']
        },
        'winter_cool': {
            'title': '21호 겨울 쿨톤 ❄️',
            'desc': "도시적이고 시크한 당신! 쿨 로즈, 블루톤 레드, 베리, 블랙/네이비 계열이 또렷한 인상을 완성해줘요.",
            'base' : {'지성': ['P001', 'P002'], '건성': ['P003', 'P004'], '복합성': ['P005', 'P006'], '민감성': ['P007', 'P008']},
            'color': {'eye': ['P009', 'P010'], 'lip': ['P011', 'P012', 'P013']}, 'makeup_styles': ['M001', 'M002', 'M003']
        }
    }
}
ALL_PRODUCTS = {
    'P001': {'brand': '헤라', 'name': '블랙 쿠션 (17N1)', 'type': '쿠션', 'price': '60,000원', 'desc': '세미매트 피니쉬로 보송하고 완벽한 커버력을 자랑하는 베스트셀러 쿠션입니다.', 'image': 'product_01.jpg'},
    'P002': {'brand': '에스티로더', 'name': '더블웨어 파운데이션 (포슬린)', 'type': '파운데이션', 'price': '82,000원', 'desc': '24시간 무너짐 없는 지속력과 완벽한 커버력의 지성 피부 추천 파운데이션입니다.', 'image': 'product_02.jpg'},
    'P003': {'brand': '에스쁘아', 'name': '프로 테일러 비글로우 쿠션', 'type': '쿠션', 'price': '35,000원', 'desc': '촉촉하고 맑은 피부 표현을 위한 건성 피부 추천 글로우 쿠션입니다.', 'image': 'product_03.jpg'},
    'P004': {'brand': '바비브라운', 'name': '인텐시브 스킨 세럼 파운데이션', 'type': '파운데이션', 'price': '95,000원', 'desc': '스킨케어 성분이 함유되어 피부 본연의 광채를 살려주는 세럼 파운데이션입니다.', 'image': 'product_04.jpg'},
    'P005': {'brand': '정샘물', 'name': '스킨 누더 커버레이어 쿠션', 'type': '쿠션', 'price': '42,000원', 'desc': '얇게 발리면서도 뛰어난 커버력으로 복합성 피부의 유수분 밸런스를 잡아줍니다.', 'image': 'product_05.jpg'},
    'P006': {'brand': '나스', 'name': '네츄럴 래디언트 롱웨어 파운데이션', 'type': '파운데이션', 'price': '72,000원', 'desc': '가벼운 발림성과 뛰어난 지속력으로 복합성 피부에 사랑받는 제품입니다.', 'image': 'product_06.jpg'},
    'P007': {'brand': '클라뷰', 'name': '어반 펄세이션 실크 쿠션', 'type': '쿠션', 'price': '32,000원', 'desc': '민감성 피부를 위한 진정 성분이 포함된 저자극 실크광 쿠션입니다.', 'image': 'product_07.jpg'},
    'P008': {'brand': '라로슈포제', 'name': '똘러리앙 뗑 플루이드', 'type': '파운데이션', 'price': '34,000원', 'desc': '민감성 피부도 안심하고 사용할 수 있는 더마 파운데이션입니다.', 'image': 'product_08.jpg'},
    'P009': {'brand': '데이지크', 'name': '섀도우 팔레트', 'type': '아이섀도우', 'price': '34,000원', 'desc': '봄웜톤의 데일리 메이크업에 최적화된 누드톤과 글리터 조합의 팔레트입니다.', 'image': 'product_09.jpg'},
    'P010': {'brand': '클리오', 'name': '킬브로우 오토 하드 브로우 펜슬', 'type': '아이브로우', 'price': '14,000원', 'desc': '뭉침 없이 자연스럽게 그려지는 하드 타입의 오토 브로우 펜슬입니다.', 'image': 'product_10.jpg'},
    'P011': {'brand': '페리페라', 'name': '잉크 더 에어리 벨벳', 'type': '립틴트', 'price': '9,000원', 'desc': '공기처럼 가벼운 텍스처와 화사한 코랄 컬러가 얼굴에 형광등을 켜줍니다.', 'image': 'product_11.jpg'},
    'P012': {'brand': '롬앤', 'name': '쥬시 래스팅 틴트', 'type': '립틴트', 'price': '9,900원', 'desc': '차분한 코랄 컬러로 데일리로 사용하기 좋은 촉촉한 광택 틴트입니다.', 'image': 'product_12.jpg'},
    'P013': {'brand': '맥', 'name': '파우더 키스 립스틱', 'type': '립스틱', 'price': '36,000원', 'desc': '부드러운 발림성과 포근한 피치 누드 컬러가 매력적인 웜톤 MLBB 립스틱입니다.', 'image': 'product_13.jpg'},
}
ALL_MAKEUP_STYLES = {
    'M001': {'style': '청순', 'title': '과즙팡! 복숭아 메이크업', 'desc': '봄웜의 정석! 사랑스러운 코랄 컬러를 활용해 화사하고 생기 넘치는 룩을 연출해보세요.', 'youtube_id': 'x912V5l-8bA'},
    'M002': {'style': '시크', 'title': '분위기 있는 세미 스모키', 'desc': '골드와 브라운의 조화로 깊이감 있는 눈매를 연출하여 성숙하고 세련된 느낌을 더합니다.', 'youtube_id': 'u9wQtj2y254'},
    'M003': {'style': '데일리', 'title': '꾸안꾸 코랄 브라운 메이크업', 'desc': '누구나 쉽게 따라할 수 있는 데일리 메이크업! 자연스러운 음영으로 매일매일 예뻐지세요.', 'youtube_id': '045La2m2mJg'},
}

class DatabaseManager:
    def __init__(self, db_name='data/beauty.db'):
        self.db_name = db_name
        self.create_db()

    def create_db(self):
        db_folder = 'data'
        if not os.path.exists(db_folder):
            os.makedirs(db_folder)

        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        # 테이블이 이미 존재하면 삭제하고 다시 생성 (데이터 초기화)
        cursor.execute("DROP TABLE IF EXISTS products")

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                brand TEXT,
                price TEXT,
                image TEXT,
                description TEXT,
                type TEXT,
                category TEXT,
                skin_types TEXT,
                personal_colors TEXT,
                style_videos TEXT
            )
        ''')
        
        # 데이터 삽입 로직
        for pid, p in ALL_PRODUCTS.items():
            personal_colors = []
            skin_types = []
            
            # BEAUTY_DATA에서 personal_colors와 skin_types 정보 찾기
            for tone_num, colors in BEAUTY_DATA.items():
                for color_name, data in colors.items():
                    # 베이스 제품
                    if 'base' in data and pid in [item for sublist in data['base'].values() for item in sublist]:
                        personal_colors.append(f"{tone_num}_{color_name}")
                        for skin_type, pids in data['base'].items():
                            if pid in pids:
                                skin_types.append(skin_type)
                    # 색조 제품
                    if 'color' in data and (pid in data['color']['eye'] or pid in data['color']['lip']):
                        personal_colors.append(f"{tone_num}_{color_name}")
            
            personal_colors = list(set(personal_colors))
            skin_types = list(set(skin_types))

            cursor.execute('''
                INSERT INTO products (name, brand, price, image, description, type, category, skin_types, personal_colors)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                p['name'], 
                p['brand'], 
                p['price'], 
                p['image'], 
                p['desc'], 
                p['type'],
                '베이스' if len(skin_types) > 0 else '색조',
                ','.join(skin_types),
                ','.join(personal_colors)
            ))

        conn.commit()
        conn.close()

    def get_beauty_data(self, tone, color):
        conn = sqlite3.connect(self.db_name)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        tone = str(tone)
        tone_for_query = tone if tone in ('20','21') else '21'
        personal_color_str = f"{tone_for_query}_{color}"

        results = []
        cursor.execute("SELECT * FROM products WHERE personal_colors LIKE ?", (f"%{personal_color_str}%",))
        results = [dict(row) for row in cursor.fetchall()]

        conn.close()

        if results:
            return {
                'title': f"{tone} {color}",
                'desc': '당신의 퍼스널 컬러에 맞는 제품을 추천합니다.',
                'products': results
            }
        return None
    
    def get_products_by_name(self, product_name):
        conn = sqlite3.connect(self.db_name)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        search_name = product_name.replace(' ', '').replace('\n', '')
        
        query = "SELECT * FROM products WHERE REPLACE(name, ' ', '') LIKE ?"
        cursor.execute(query, (f'%{search_name}%',))
        
        result = cursor.fetchone()
        conn.close()
        return dict(result) if result else None

if __name__ == '__main__':
    dm = DatabaseManager()
    print("Database 'beauty.db' created and populated with sample data successfully.")


def get_product_by_name(self, product_name):
    """Compatibility alias for singular lookup."""
    return self.get_products_by_name(product_name)


def get_products_by_filter(self, personal_color=None, skin_type=None, exclude_id=None, limit=6):
    """Filter products by personal_color (e.g., 'spring_warm') and skin_type (e.g., '지성')."""
    import sqlite3
    conn = sqlite3.connect(self.db_name); conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    where = []; params = []
    if personal_color:
        where.append("personal_colors LIKE ?"); params.append("%%_%s%%" % personal_color)
    if skin_type:
        where.append("skin_types LIKE ?"); params.append("%%%s%%" % skin_type)
    if exclude_id is not None:
        where.append("id != ?"); params.append(exclude_id)
    where_sql = (" WHERE " + " AND ".join(where)) if where else ""
    sql = "SELECT * FROM products%s LIMIT ?" % where_sql
    params.append(int(limit))
    cur.execute(sql, tuple(params))
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows
