"""
Tests for MCP Continuity Service
"""

import pytest
import asyncio
from src.core.continuity_manager import ContinuityManager
from src.core.context_detector import ContextDetector
from src.core.session_manager import SessionManager

class TestContextDetector:
    """Test context detection functionality"""
    
    def setup_method(self):
        self.detector = ContextDetector()
    
    @pytest.mark.asyncio
    async def test_portuguese_continuity_questions(self):
        """Test Portuguese continuity question detection"""
        questions = [
            "onde paramos?",
            "onde paramos",
            "o que estávamos fazendo?",
            "continue de onde parou",
            "qual o status do projeto?"
        ]
        
        for question in questions:
            result = await self.detector.is_continuity_question(question)
            assert result == True, f"Failed to detect: {question}"
    
    @pytest.mark.asyncio
    async def test_english_continuity_questions(self):
        """Test English continuity question detection"""
        questions = [
            "where did we leave off?",
            "what were we doing?",
            "continue from where we stopped",
            "resume session"
        ]
        
        for question in questions:
            result = await self.detector.is_continuity_question(question)
            assert result == True, f"Failed to detect: {question}"
    
    @pytest.mark.asyncio
    async def test_non_continuity_questions(self):
        """Test that normal questions are not detected as continuity"""
        normal_questions = [
            "How are you?",
            "What is Python?",
            "Explain machine learning",
            "Create a function"
        ]
        
        for question in normal_questions:
            result = await self.detector.is_continuity_question(question)
            assert result == False, f"Incorrectly detected: {question}"

class TestSessionManager:
    """Test session management functionality"""
    
    def setup_method(self):
        self.manager = SessionManager()
    
    @pytest.mark.asyncio
    async def test_create_session(self):
        """Test session creation"""
        session_id = await self.manager.create_session()
        assert session_id is not None
        assert len(session_id) > 0
        
        # Check session exists
        session = await self.manager.get_session(session_id)
        assert session is not None
        assert session['id'] == session_id
    
    @pytest.mark.asyncio
    async def test_save_input(self):
        """Test input preservation"""
        session_id = await self.manager.create_session()
        test_input = "This is a test input"
        
        await self.manager.save_input(test_input, session_id)
        
        session = await self.manager.get_session(session_id)
        assert len(session['inputs']) > 0
        assert session['inputs'][-1]['content'] == test_input

class TestContinuityManager:
    """Test main continuity manager functionality"""
    
    def setup_method(self):
        self.manager = ContinuityManager()
    
    @pytest.mark.asyncio
    async def test_process_continuity_question(self):
        """Test processing of continuity questions"""
        result = await self.manager.process_user_input(
            "onde paramos?",
            "test-session"
        )
        
        assert result['type'] == 'continuity_response'
        assert 'session_id' in result
        assert 'timestamp' in result
    
    @pytest.mark.asyncio
    async def test_process_normal_input(self):
        """Test processing of normal input"""
        result = await self.manager.process_user_input(
            "Hello, how are you?",
            "test-session"
        )
        
        assert result['type'] == 'session_continue'
        assert result['user_input'] == "Hello, how are you?"

# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
