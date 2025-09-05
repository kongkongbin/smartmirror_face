from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QScrollArea, QFrame, QGridLayout, QHBoxLayout, QSizePolicy, QSpacerItem
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QImage, QFont

class FaceResultPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignCenter)

        # 결과 타이틀 및 설명
        self.result_title = QLabel("🎉 분석 완료!", objectName="h2")
        self.result_desc = QLabel("AI가 분석한 당신의 결과는...", objectName="desc")
        self.result_desc.setAlignment(Qt.AlignCenter)
        
        # 퍼스널 컬러 결과
        self.user_tone_label = QLabel("퍼스널 컬러 결과", objectName="h3")
        self.user_color_desc = QLabel("결과 설명", objectName="desc")
        
        # 추천 제품 그리드
        self.product_grid = QGridLayout()
        product_container = QWidget()
        product_container.setLayout(self.product_grid)
        
        # 스크롤 영역
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(product_container)
        
        # 돌아가기 버튼
        self.go_home_btn = QPushButton("처음으로")
        self.go_home_btn.setFixedSize(300, 100)
        self.go_home_btn.setObjectName("home_btn")

        main_layout.addWidget(self.result_title)
        main_layout.addWidget(self.result_desc)
        main_layout.addStretch()
        main_layout.addWidget(self.user_tone_label)
        main_layout.addWidget(self.user_color_desc)
        main_layout.addStretch()
        main_layout.addWidget(scroll_area)
        main_layout.addWidget(self.go_home_btn)
    
    def update_result(self, data):
        # 기존 제품 카드 삭제
        self.clear_layout(self.product_grid)
        
        # 결과 화면 업데이트
        self.user_tone_label.setText(data.get('title', ''))
        self.user_color_desc.setText(data.get('desc', ''))
        
        # 추천 제품 카드 추가
        products = data.get('products') or []
        if not products:
            empty = QLabel("표시할 추천 제품이 아직 없어요.", objectName="desc")
            empty.setAlignment(Qt.AlignCenter)
            self.product_grid.addWidget(empty, 0, 0)
            return
        for i, product in enumerate(products):
            self.create_product_card(product, self.product_grid, i)

    def create_product_card(self, product, layout, index):
        card = QFrame()
        card.setStyleSheet("QFrame { border: 1px solid #ddd; border-radius: 10px; padding: 10px; }")
        card_layout = QVBoxLayout(card)
        
        title = QLabel(f"{product.get('brand','')} · {product.get('name','')}")
        meta = QLabel(" | ".join(filter(None, [product.get('type',''), product.get('price','')])))
        desc = QLabel(product.get('description', ''))
        desc.setWordWrap(True)
        
        card_layout.addWidget(title)
        card_layout.addWidget(meta)
        card_layout.addWidget(desc)
        
        layout.addWidget(card, index // 2, index % 2)

    def clear_layout(self, layout):
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()

class ProductRecommendPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignCenter)
        
        self.recommend_title = QLabel("📦 추천 제품", objectName="h2")
        self.product_grid = QGridLayout()
        product_container = QWidget()
        product_container.setLayout(self.product_grid)
        
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(product_container)
        
        self.go_home_btn = QPushButton("처음으로")
        self.go_home_btn.setFixedSize(300, 100)
        self.go_home_btn.setObjectName("home_btn")

        main_layout.addWidget(self.recommend_title)
        main_layout.addWidget(scroll_area)
        main_layout.addWidget(self.go_home_btn)

    def update_recommendations(self, data: dict):
        # data = {'found_product': {...}, 'recommendations': [...]}
        self.clear_layout(self.product_grid)

        found = data.get('found_product')
        recs = data.get('recommendations') or []

        row = 0
        if found:
            header = QLabel("🔎 인식된 제품", objectName="h3")
            self.product_grid.addWidget(header, row, 0, 1, 2); row += 1
            self._add_card(found, row, 0, span=2); row += 2  # 여백 포함

        header2 = QLabel("✨ 비슷한 추천 제품", objectName="h3")
        self.product_grid.addWidget(header2, row, 0, 1, 2); row += 1

        if not recs:
            empty = QLabel("추천 제품이 아직 없어요.", objectName="desc")
            empty.setAlignment(Qt.AlignCenter)
            self.product_grid.addWidget(empty, row, 0, 1, 2)
            return

        for i, p in enumerate(recs):
            r = row + (i // 2)
            c = i % 2
            self._add_card(p, r, c)

    def _add_card(self, product, r, c, span=1):
        card = QFrame()
        card.setStyleSheet("QFrame { border: 1px solid #ddd; border-radius: 10px; padding: 10px; }")
        v = QVBoxLayout(card)
        title = QLabel(f"{product.get('brand','')} · {product.get('name','')}")
        meta = QLabel(" | ".join(filter(None, [product.get('type',''), product.get('price','')])))
        desc = QLabel(product.get('description', ''))
        desc.setWordWrap(True)
        v.addWidget(title); v.addWidget(meta); v.addWidget(desc)
        self.product_grid.addWidget(card, r, c, 1, span)

    def clear_layout(self, layout):
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()