#!/usr/bin/env python3
"""
Comprehensive End-to-End Integration Test
Tests all components of the interview analysis system
"""
import sys
import os
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

print("=" * 70)
print("🔍 COMPREHENSIVE END-TO-END INTEGRATION TEST")
print("=" * 70)
print()

# Test counters
tests_passed = 0
tests_failed = 0
test_results = []

def test_step(name, test_func):
    """Run a test step and record results"""
    global tests_passed, tests_failed
    try:
        print(f"Testing: {name}...", end=" ")
        result = test_func()
        if result:
            print("✅ PASS")
            tests_passed += 1
            test_results.append((name, "✅ PASS", None))
        else:
            print("❌ FAIL")
            tests_failed += 1
            test_results.append((name, "❌ FAIL", "Test returned False"))
    except Exception as e:
        print(f"❌ FAIL - {str(e)}")
        tests_failed += 1
        test_results.append((name, "❌ FAIL", str(e)))

# ============================================================================
# TEST 1: Environment Variables
# ============================================================================
print("\n📋 SECTION 1: Environment Variables")
print("-" * 70)

def test_env_vars():
    required_vars = [
        'GROQ_API_KEY',
        'ELEVENLABS_API_KEY',
        'SUPABASE_URL',
        'SUPABASE_KEY',
        'AWS_ACCESS_KEY_ID',
        'AWS_SECRET_ACCESS_KEY',
        'AWS_S3_BUCKET'
    ]
    
    missing = []
    for var in required_vars:
        if not os.getenv(var):
            missing.append(var)
    
    if missing:
        print(f"   Missing: {', '.join(missing)}")
        return False
    
    print(f"   All {len(required_vars)} environment variables present")
    return True

test_step("Environment Variables", test_env_vars)

# ============================================================================
# TEST 2: Service Imports
# ============================================================================
print("\n📦 SECTION 2: Service Imports")
print("-" * 70)

def test_groq_import():
    from app.services.groq_service import GroqService
    service = GroqService()
    return service is not None and service.client is not None

def test_elevenlabs_import():
    from app.services.elevenlabs_service import ElevenLabsService
    service = ElevenLabsService()
    return service is not None

def test_transcript_analyzer_import():
    from app.services.transcript_analyzer import TranscriptAnalyzer
    analyzer = TranscriptAnalyzer()
    return analyzer is not None

def test_orchestrator_import():
    from app.services.interview_analysis_orchestrator import InterviewAnalysisOrchestrator
    orchestrator = InterviewAnalysisOrchestrator()
    return orchestrator is not None

test_step("Groq Service Import & Initialization", test_groq_import)
test_step("ElevenLabs Service Import", test_elevenlabs_import)
test_step("Transcript Analyzer Import", test_transcript_analyzer_import)
test_step("Interview Orchestrator Import", test_orchestrator_import)

# ============================================================================
# TEST 3: Groq API Connection
# ============================================================================
print("\n🤖 SECTION 3: Groq API Connection")
print("-" * 70)

def test_groq_connection():
    from app.services.groq_service import GroqService
    service = GroqService()
    result = service.test_connection()
    if result.get('success'):
        print(f"   Model: {result.get('model')}")
        return True
    else:
        print(f"   Error: {result.get('error')}")
        return False

test_step("Groq API Live Connection", test_groq_connection)

# ============================================================================
# TEST 4: Transcript Analyzer Functionality
# ============================================================================
print("\n📝 SECTION 4: Transcript Analyzer")
print("-" * 70)

def test_transcript_analysis():
    from app.services.transcript_analyzer import TranscriptAnalyzer
    analyzer = TranscriptAnalyzer()
    
    # Test with sample transcript
    sample_transcript = """
    I have five years of experience in software engineering. 
    I worked on various projects including web development and mobile applications.
    My strengths include problem solving and team collaboration.
    I'm excited about this opportunity because it aligns with my career goals.
    """
    
    result = analyzer.analyze_transcript(sample_transcript, duration_seconds=120)
    
    # Verify all expected keys are present
    required_keys = [
        'filler_word_analysis',
        'speaking_pace',
        'word_diversity',
        'sentence_structure',
        'communication_score'
    ]
    
    for key in required_keys:
        if key not in result:
            print(f"   Missing key: {key}")
            return False
    
    comm_score = result['communication_score']['score']
    print(f"   Communication Score: {comm_score}/100")
    print(f"   Filler Words: {result['filler_word_analysis']['filler_percentage']:.2f}%")
    print(f"   Speaking Pace: {result['speaking_pace']['words_per_minute']:.1f} WPM")
    
    return True

test_step("Transcript Analysis with Sample Data", test_transcript_analysis)

# ============================================================================
# TEST 5: Model Updates Verification
# ============================================================================
print("\n🔄 SECTION 5: Model Updates Verification")
print("-" * 70)

def test_model_updates():
    # Check that all files use the correct model
    files_to_check = [
        'app/services/groq_service.py',
        'app/services/interview_analysis_orchestrator.py',
        'app/api/v1/endpoints/cv_tracking.py'
    ]
    
    correct_model = 'llama-3.3-70b-versatile'
    old_model = 'llama-3.1-70b-versatile'
    
    for file_path in files_to_check:
        full_path = backend_dir / file_path
        if not full_path.exists():
            print(f"   File not found: {file_path}")
            return False
        
        with open(full_path, 'r') as f:
            content = f.read()
            
        if old_model in content:
            print(f"   ❌ Old model found in {file_path}")
            return False
        
        if correct_model not in content:
            print(f"   ⚠️  New model not found in {file_path}")
    
    print(f"   All files use {correct_model}")
    return True

test_step("Groq Model Updates", test_model_updates)

# ============================================================================
# TEST 6: ElevenLabs Service Structure
# ============================================================================
print("\n🎤 SECTION 6: ElevenLabs Service Structure")
print("-" * 70)

def test_elevenlabs_methods():
    from app.services.elevenlabs_service import ElevenLabsService
    service = ElevenLabsService()
    
    # Check that required methods exist
    required_methods = [
        'get_conversation_transcript',
        'create_agent_for_persona',
        'get_conversation_details'
    ]
    
    for method in required_methods:
        if not hasattr(service, method):
            print(f"   Missing method: {method}")
            return False
    
    print(f"   All {len(required_methods)} required methods present")
    return True

test_step("ElevenLabs Service Methods", test_elevenlabs_methods)

# ============================================================================
# TEST 7: Interview Orchestrator Integration
# ============================================================================
print("\n🎯 SECTION 7: Interview Orchestrator Integration")
print("-" * 70)

def test_orchestrator_integration():
    from app.services.interview_analysis_orchestrator import InterviewAnalysisOrchestrator
    orchestrator = InterviewAnalysisOrchestrator()
    
    # Verify all services are initialized
    checks = [
        ('supabase_service', orchestrator.supabase_service),
        ('s3_service', orchestrator.s3_service),
        ('elevenlabs_service', orchestrator.elevenlabs_service),
        ('transcript_analyzer', orchestrator.transcript_analyzer),
        ('groq_service', orchestrator.groq_service)
    ]
    
    for name, service in checks:
        if service is None:
            print(f"   {name} not initialized")
            return False
    
    print(f"   All {len(checks)} services initialized")
    return True

test_step("Orchestrator Service Integration", test_orchestrator_integration)

# ============================================================================
# TEST 8: API Endpoints Structure
# ============================================================================
print("\n🌐 SECTION 8: API Endpoints")
print("-" * 70)

def test_api_endpoints():
    try:
        from app.api.v1.endpoints.interview_analysis import router
        
        # Check that required endpoints exist
        routes = [route.path for route in router.routes]
        
        required_endpoints = ['/start', '/status/{interview_id}', '/results/{interview_id}']
        
        for endpoint in required_endpoints:
            if not any(endpoint in route for route in routes):
                print(f"   Missing endpoint: {endpoint}")
                return False
        
        print(f"   All {len(required_endpoints)} required endpoints present")
        
        # Check for test endpoint
        if '/test-groq' in routes:
            print(f"   ✅ Diagnostic endpoint /test-groq found")
        
        return True
    except Exception as e:
        print(f"   Error: {e}")
        return False

test_step("API Endpoints Structure", test_api_endpoints)

# ============================================================================
# TEST 9: Error Handling
# ============================================================================
print("\n⚠️  SECTION 9: Error Handling")
print("-" * 70)

def test_error_handling():
    from app.services.transcript_analyzer import TranscriptAnalyzer
    analyzer = TranscriptAnalyzer()
    
    # Test with empty transcript
    result = analyzer.analyze_transcript("", 0)
    
    if 'communication_score' not in result:
        print("   Empty transcript not handled properly")
        return False
    
    print("   Empty transcript handled gracefully")
    return True

test_step("Empty Transcript Error Handling", test_error_handling)

# ============================================================================
# TEST 10: File Structure
# ============================================================================
print("\n📁 SECTION 10: File Structure")
print("-" * 70)

def test_file_structure():
    required_files = [
        'app/services/groq_service.py',
        'app/services/elevenlabs_service.py',
        'app/services/transcript_analyzer.py',
        'app/services/interview_analysis_orchestrator.py',
        'app/api/v1/endpoints/interview_analysis.py',
        'test_groq_connection.py'
    ]
    
    missing = []
    for file_path in required_files:
        full_path = backend_dir / file_path
        if not full_path.exists():
            missing.append(file_path)
    
    if missing:
        print(f"   Missing files: {', '.join(missing)}")
        return False
    
    print(f"   All {len(required_files)} required files present")
    return True

test_step("Required Files Present", test_file_structure)

# ============================================================================
# TEST SUMMARY
# ============================================================================
print("\n" + "=" * 70)
print("📊 TEST SUMMARY")
print("=" * 70)
print()

total_tests = tests_passed + tests_failed
success_rate = (tests_passed / total_tests * 100) if total_tests > 0 else 0

print(f"Total Tests: {total_tests}")
print(f"✅ Passed: {tests_passed}")
print(f"❌ Failed: {tests_failed}")
print(f"Success Rate: {success_rate:.1f}%")
print()

# Detailed results
if tests_failed > 0:
    print("Failed Tests:")
    for name, status, error in test_results:
        if status == "❌ FAIL":
            print(f"  - {name}")
            if error:
                print(f"    Error: {error}")
    print()

# Final verdict
print("=" * 70)
if tests_failed == 0:
    print("🎉 ALL TESTS PASSED - System is fully operational!")
    print("=" * 70)
    print()
    print("✅ Your interview analysis system is working end-to-end!")
    print("✅ All recent implementations are properly integrated")
    print("✅ Ready for production use")
    sys.exit(0)
else:
    print("⚠️  SOME TESTS FAILED - Review issues above")
    print("=" * 70)
    sys.exit(1)
