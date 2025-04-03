class InsuranceProfile:
    """
    한화손해보험 운전자보험 상담을 위한 고객 프로필 클래스
    대화 내용에서 추출한 정보를 업데이트하며 최적의 운전자보험 상담에 활용
    """
    def __init__(self):
        # 기본 인적사항 (핵심만 유지)
        self.name = None                  # 고객 이름
        self.age = None                   # 나이
        self.gender = None                # 성별
        self.occupation = None            # 직업
        
        # 운전 관련 정보
        self.driving_experience = None    # 운전 경력(년)
        self.vehicle_type = None          # 차량 종류(승용차/SUV/트럭 등)
        self.annual_mileage = None        # 연간 주행거리
        self.accident_history = []        # 사고 이력
        self.traffic_violations = []      # 교통법규 위반 이력
        self.commute_distance = None      # 출퇴근 거리
        self.main_driving_area = None     # 주 운전지역(도심/고속도로/시외 등)
        
        # 보험 관련 정보
        self.current_insurance = None     # 현재 자동차보험 가입 여부
        self.current_driver_insurance = None  # 현재 운전자보험 가입 여부
        self.budget_monthly = None        # 보험료 예산(월)
        self.coverage_preference = None   # 보장범위 선호(최소/일반/프리미엄)
        
        # 운전자보험 니즈
        self.priority_coverage = []       # 우선적으로 원하는 보장(교통사고처리지원금/벌금/변호사선임 등)
        self.pain_points = []             # 고객이 언급한 페인 포인트
        
        # 한화손해보험 관련 정보
        self.hanwha_customer_id = None    # 한화손해보험 고객 ID (기존 고객인 경우)
        self.inquiry_products = []        # 고객이 문의한 한화 운전자보험 상품
        self.preferred_contact_method = None  # 선호하는 연락 방식
        
    def update(self, extracted_info):
        """
        대화에서 추출한 정보로 프로필 업데이트
        
        Args:
            extracted_info (dict): 대화에서 추출한 고객 정보
        
        Returns:
            self: 업데이트된 프로필 객체
        """
        # 딕셔너리의 키가 있으면 해당 속성 업데이트
        for key, value in extracted_info.items():
            if hasattr(self, key) and value:
                if isinstance(getattr(self, key), list) and not isinstance(value, list):
                    # 리스트 속성에 단일 값 추가
                    getattr(self, key).append(value)
                else:
                    # 일반 속성 업데이트 또는 리스트 속성에 리스트 할당
                    setattr(self, key, value)
        
        return self
    
    def get_missing_critical_info(self):
        """
        운전자보험 상담을 위해 꼭 필요한 누락된 정보 목록 반환
        
        Returns:
            list: 누락된 중요 정보 필드 목록
        """
        critical_fields = {
            'age': '고객님의 연령대',
            'driving_experience': '운전 경력',
            'vehicle_type': '차량 종류',
            'commute_distance': '출퇴근 거리',
            'current_driver_insurance': '현재 운전자보험 가입 여부'
        }
        
        missing = []
        for field, display_name in critical_fields.items():
            if getattr(self, field) is None:
                missing.append((field, display_name))
                
        return missing
    
    def to_dict(self):
        """
        프로필을 딕셔너리 형태로 변환 (카테고리별로 구성)
        
        Returns:
            dict: 프로필 정보를 담은 딕셔너리
        """
        profile_dict = {}
        
        # 인적사항 섹션
        personal_info = {key: getattr(self, key) for key in 
                         ['name', 'age', 'gender', 'occupation']}
        profile_dict["인적사항"] = {k: v for k, v in personal_info.items() if v is not None}
        
        # 운전관련 정보 섹션
        driving_info = {key: getattr(self, key) for key in 
                       ['driving_experience', 'vehicle_type', 'annual_mileage', 
                        'accident_history', 'traffic_violations', 'commute_distance',
                        'main_driving_area']}
        profile_dict["운전정보"] = {k: v for k, v in driving_info.items() if v is not None}
        
        # 보험관련 정보 섹션
        insurance_info = {key: getattr(self, key) for key in 
                          ['current_insurance', 'current_driver_insurance', 
                           'budget_monthly', 'coverage_preference']}
        profile_dict["보험정보"] = {k: v for k, v in insurance_info.items() if v is not None}
        
        # 운전자보험 니즈 섹션
        needs_info = {key: getattr(self, key) for key in 
                      ['priority_coverage', 'pain_points']}
        profile_dict["운전자보험니즈"] = {k: v for k, v in needs_info.items() if v is not None}
        
        # 한화손해보험 관련 정보
        hanwha_info = {key: getattr(self, key) for key in 
                       ['hanwha_customer_id', 'inquiry_products', 'preferred_contact_method']}
        profile_dict["한화손해보험정보"] = {k: v for k, v in hanwha_info.items() if v is not None}
        
        return profile_dict
    
    def __str__(self):
        """
        프로필을 문자열로 표현
        
        Returns:
            str: 프로필 정보 문자열
        """
        profile_dict = self.to_dict()
        
        result = "====== 운전자보험 고객 프로필 ======\n"
        for section, items in profile_dict.items():
            if items:  # 섹션에 데이터가 있는 경우만 포함
                result += f"\n▶ {section}\n"
                for key, value in items.items():
                    result += f"  • {key}: {value}\n"
        
        # 중요 누락 정보 표시
        missing_info = self.get_missing_critical_info()
        if missing_info:
            result += "\n▶ 누락된 중요 정보\n"
            for field, display_name in missing_info:
                result += f"  • {display_name}\n"
        
        return result 