from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QScrollArea, QFrame, QGridLayout, QHBoxLayout
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
        if 'products' in data:
            for i, product in enumerate(data['products']):
                self.create_product_card(product, self.product_grid, i)

    def create_product_card(self, product, layout, index):
        card = QFrame()
        card.setStyleSheet("QFrame { border: 1px solid #ddd; border-radius: 10px; padding: 10px; }")
        card_layout = QVBoxLayout(card)
        
        name_label = QLabel(product.get('name', ''))
        desc_label = QLabel(product.get('description', ''))
        
        card_layout.addWidget(name_label)
        card_layout.addWidget(desc_label)
        
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