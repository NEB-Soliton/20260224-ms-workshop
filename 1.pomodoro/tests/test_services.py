"""
Unit tests for Gamification Engine Service Layer
ゲーミフィケーションエンジンのサービス層の単体テスト
"""
import pytest
from datetime import datetime, timedelta
from pomodoro.services import GamificationEngine


class TestGamificationEngine:
    """Test suite for GamificationEngine"""
    
    def test_calculate_level_from_zero_xp(self):
        """Test level calculation with 0 XP"""
        engine = GamificationEngine()
        assert engine.calculate_level(0) == 1
    
    def test_calculate_level_basic(self):
        """Test basic level calculations"""
        engine = GamificationEngine()
        
        # Level 1: 0-199 XP
        assert engine.calculate_level(100) == 1
        assert engine.calculate_level(199) == 1
        
        # Level 2: 200-599 XP (200 + 400)
        assert engine.calculate_level(200) == 2
        assert engine.calculate_level(400) == 2
        
        # Level 3: 600-1199 XP (200 + 400 + 600)
        assert engine.calculate_level(600) == 3
        assert engine.calculate_level(800) == 3
    
    def test_calculate_xp_for_level(self):
        """Test XP threshold calculation for specific levels"""
        engine = GamificationEngine()
        
        assert engine.calculate_xp_for_level(1) == 0
        assert engine.calculate_xp_for_level(2) == 200   # 1*200
        assert engine.calculate_xp_for_level(3) == 600   # 1*200 + 2*200
        assert engine.calculate_xp_for_level(4) == 1200  # 1*200 + 2*200 + 3*200
    
    def test_calculate_rewards_no_sessions(self):
        """Test rewards calculation with no sessions"""
        engine = GamificationEngine()
        rewards = engine.calculate_rewards([])
        
        assert rewards['xp'] == 0
        assert rewards['level'] == 1
        assert rewards['streak'] == 0
        assert rewards['streak_bonus'] == 0
        assert rewards['badges'] == []
        assert rewards['completed_count'] == 0
    
    def test_calculate_rewards_single_session(self):
        """Test rewards calculation with single completed session"""
        engine = GamificationEngine()
        sessions = [
            {
                'completed': True,
                'timestamp': datetime.utcnow().isoformat()
            }
        ]
        
        rewards = engine.calculate_rewards(sessions)
        
        assert rewards['xp'] == 100  # Base XP for 1 completion
        assert rewards['level'] == 1
        assert rewards['completed_count'] == 1
    
    def test_calculate_rewards_multiple_sessions(self):
        """Test rewards calculation with multiple sessions"""
        engine = GamificationEngine()
        sessions = [
            {'completed': True, 'timestamp': datetime.utcnow().isoformat()}
            for _ in range(5)
        ]
        
        rewards = engine.calculate_rewards(sessions)
        
        assert rewards['xp'] == 500  # 5 * 100
        assert rewards['level'] == 2  # 500 XP is level 2
        assert rewards['completed_count'] == 5
    
    def test_calculate_rewards_ignores_incomplete_sessions(self):
        """Test that incomplete sessions are not counted"""
        engine = GamificationEngine()
        sessions = [
            {'completed': True, 'timestamp': datetime.utcnow().isoformat()},
            {'completed': False, 'timestamp': datetime.utcnow().isoformat()},
            {'completed': True, 'timestamp': datetime.utcnow().isoformat()},
        ]
        
        rewards = engine.calculate_rewards(sessions)
        
        assert rewards['completed_count'] == 2
        assert rewards['xp'] == 200
    
    def test_streak_calculation_no_streak(self):
        """Test streak calculation with no consecutive days"""
        engine = GamificationEngine()
        old_date = (datetime.utcnow() - timedelta(days=5)).isoformat()
        sessions = [
            {'completed': True, 'timestamp': old_date}
        ]
        
        rewards = engine.calculate_rewards(sessions)
        assert rewards['streak'] == 0
    
    def test_streak_calculation_today_only(self):
        """Test streak with sessions only today"""
        engine = GamificationEngine()
        today = datetime.utcnow().isoformat()
        sessions = [
            {'completed': True, 'timestamp': today},
            {'completed': True, 'timestamp': today},
        ]
        
        rewards = engine.calculate_rewards(sessions)
        assert rewards['streak'] == 1
    
    def test_streak_calculation_consecutive_days(self):
        """Test streak with consecutive days"""
        engine = GamificationEngine()
        now = datetime.utcnow()
        sessions = [
            {'completed': True, 'timestamp': now.isoformat()},
            {'completed': True, 'timestamp': (now - timedelta(days=1)).isoformat()},
            {'completed': True, 'timestamp': (now - timedelta(days=2)).isoformat()},
        ]
        
        rewards = engine.calculate_rewards(sessions)
        assert rewards['streak'] == 3
    
    def test_streak_calculation_broken_streak(self):
        """Test streak with broken consecutive days"""
        engine = GamificationEngine()
        now = datetime.utcnow()
        sessions = [
            {'completed': True, 'timestamp': now.isoformat()},
            {'completed': True, 'timestamp': (now - timedelta(days=1)).isoformat()},
            # Day 2 missing - breaks streak
            {'completed': True, 'timestamp': (now - timedelta(days=3)).isoformat()},
        ]
        
        rewards = engine.calculate_rewards(sessions)
        assert rewards['streak'] == 2
    
    def test_streak_bonus_3_days(self):
        """Test streak bonus for 3 consecutive days"""
        engine = GamificationEngine()
        now = datetime.utcnow()
        sessions = [
            {'completed': True, 'timestamp': now.isoformat()},
            {'completed': True, 'timestamp': (now - timedelta(days=1)).isoformat()},
            {'completed': True, 'timestamp': (now - timedelta(days=2)).isoformat()},
        ]
        
        rewards = engine.calculate_rewards(sessions)
        assert rewards['streak'] == 3
        assert rewards['streak_bonus'] == 50
        assert rewards['xp'] == 350  # 300 base + 50 bonus
    
    def test_streak_bonus_7_days(self):
        """Test streak bonus for 7 consecutive days"""
        engine = GamificationEngine()
        now = datetime.utcnow()
        sessions = [
            {'completed': True, 'timestamp': (now - timedelta(days=i)).isoformat()}
            for i in range(7)
        ]
        
        rewards = engine.calculate_rewards(sessions)
        assert rewards['streak'] == 7
        assert rewards['streak_bonus'] == 100
        assert rewards['xp'] == 800  # 700 base + 100 bonus
    
    def test_badges_novice(self):
        """Test novice badge (10 completions)"""
        engine = GamificationEngine()
        sessions = [
            {'completed': True, 'timestamp': datetime.utcnow().isoformat()}
            for _ in range(10)
        ]
        
        rewards = engine.calculate_rewards(sessions)
        badge_ids = [b['id'] for b in rewards['badges']]
        
        assert 'novice' in badge_ids
        assert 'intermediate' not in badge_ids
    
    def test_badges_intermediate(self):
        """Test intermediate badge (50 completions)"""
        engine = GamificationEngine()
        sessions = [
            {'completed': True, 'timestamp': datetime.utcnow().isoformat()}
            for _ in range(50)
        ]
        
        rewards = engine.calculate_rewards(sessions)
        badge_ids = [b['id'] for b in rewards['badges']]
        
        assert 'novice' in badge_ids
        assert 'intermediate' in badge_ids
        assert 'expert' not in badge_ids
    
    def test_badges_expert(self):
        """Test expert badge (100 completions)"""
        engine = GamificationEngine()
        sessions = [
            {'completed': True, 'timestamp': datetime.utcnow().isoformat()}
            for _ in range(100)
        ]
        
        rewards = engine.calculate_rewards(sessions)
        badge_ids = [b['id'] for b in rewards['badges']]
        
        assert 'novice' in badge_ids
        assert 'intermediate' in badge_ids
        assert 'expert' in badge_ids
    
    def test_badges_streak(self):
        """Test streak badges"""
        engine = GamificationEngine()
        now = datetime.utcnow()
        
        # 7-day streak
        sessions = [
            {'completed': True, 'timestamp': (now - timedelta(days=i)).isoformat()}
            for i in range(7)
        ]
        
        rewards = engine.calculate_rewards(sessions)
        badge_ids = [b['id'] for b in rewards['badges']]
        
        assert 'streak_3' in badge_ids
        assert 'streak_7' in badge_ids
    
    def test_level_progression(self):
        """Test level progression through multiple sessions"""
        engine = GamificationEngine()
        
        # Create sessions for level progression
        # Level 2 requires 200 XP (2 sessions)
        # Level 3 requires 600 XP (6 sessions)
        sessions_level_2 = [
            {'completed': True, 'timestamp': datetime.utcnow().isoformat()}
            for _ in range(2)
        ]
        
        rewards_level_2 = engine.calculate_rewards(sessions_level_2)
        assert rewards_level_2['level'] == 2
        
        sessions_level_3 = [
            {'completed': True, 'timestamp': datetime.utcnow().isoformat()}
            for _ in range(6)
        ]
        
        rewards_level_3 = engine.calculate_rewards(sessions_level_3)
        assert rewards_level_3['level'] == 3
