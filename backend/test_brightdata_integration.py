#!/usr/bin/env python3
"""
Test script for BrightData MCP integration with Crawl4AI
Demonstrates how to use the new job scraping and analysis features.
"""

import asyncio
import json
import sys
from pathlib import Path

# Add the app directory to the Python path
sys.path.append(str(Path(__file__).parent / "app"))

from app.services.brightdata_mcp_service import BrightDataMCPService
from app.services.crawl4ai_service import Crawl4AIService
from app.services.job_market_analyzer import JobMarketAnalyzer

async def test_brightdata_service():
    """Test the BrightData MCP service"""
    print("🧪 Testing BrightData MCP Service")
    print("=" * 50)
    
    service = BrightDataMCPService()
    
    # Test 1: Basic job scraping
    print("\n📚 Test 1: Basic LinkedIn job scraping...")
    jobs = await service.scrape_linkedin_jobs(
        keywords="software engineer",
        location="San Francisco",
        max_results=5
    )
    
    if jobs['success']:
        print(f"✅ Scraped {jobs['total_jobs']} jobs")
        for i, job in enumerate(jobs['jobs'][:3], 1):
            print(f"   {i}. {job['title']} at {job['company']} ({job['location']})")
    else:
        print(f"❌ Scraping failed: {jobs['error']}")
    
    # Test 2: Skills analysis
    if jobs['success'] and jobs['jobs']:
        print("\n📊 Test 2: Skills analysis...")
        skills = service.extract_skills_from_jobs(jobs['jobs'])
        print(f"   Top skills: {list(skills.keys())[:5]}")
        
        # Test trend analysis
        trends = service.analyze_job_trends(jobs['jobs'])
        print(f"   Job types: {trends.get('job_types', {})}")
    
    # Test 3: Company-specific scraping
    print("\n🏢 Test 3: Company-specific job scraping...")
    company_jobs = await service.scrape_company_jobs("Google", max_results=3)
    
    if company_jobs['success']:
        print(f"✅ Scraped {company_jobs['total_jobs']} jobs from {company_jobs['company']}")
    else:
        print(f"❌ Company scraping failed: {company_jobs['error']}")
    
    return jobs

async def test_enhanced_crawl4ai():
    """Test the enhanced Crawl4AI service with job scraping"""
    print("\n\n🔧 Testing Enhanced Crawl4AI Service")
    print("=" * 50)
    
    async with Crawl4AIService() as service:
        # Test 1: Job-based interview prep
        print("\n🎯 Test 1: Job-based interview preparation...")
        prep = await service.scrape_jobs_for_interview_prep(
            job_title="software engineer",
            location="San Francisco",
            max_jobs=10
        )
        
        if prep['success']:
            print(f"✅ Generated {prep['total_questions']} interview questions")
            print(f"   Jobs analyzed: {prep['total_jobs']}")
            print(f"   Top skills: {list(prep['skills_analysis'].keys())[:5]}")
            
            # Show sample questions
            print("\n   Sample questions:")
            for i, q in enumerate(prep['interview_questions'][:3], 1):
                print(f"   {i}. {q['question'][:80]}...")
        else:
            print(f"❌ Interview prep failed: {prep['error']}")
        
        # Test 2: Job market insights
        print("\n📈 Test 2: Job market insights...")
        insights = await service.get_job_market_insights(
            keywords="software engineer",
            location=""
        )
        
        if insights['success']:
            print(f"✅ Generated insights from {insights['total_jobs_analyzed']} jobs")
            print(f"   Market summary: {insights['insights']['market_summary']}")
            print(f"   Top skills: {insights['insights']['top_skills'][:5]}")
        else:
            print(f"❌ Market insights failed: {insights['error']}")
        
        # Test 3: Company-specific analysis
        print("\n🏢 Test 3: Company-specific analysis...")
        company_analysis = await service.scrape_company_specific_jobs(
            company_name="Microsoft",
            generate_questions=True
        )
        
        if company_analysis['success']:
            print(f"✅ Analyzed {company_analysis['total_jobs']} jobs from {company_analysis['company']}")
            if company_analysis.get('interview_questions'):
                print(f"   Generated {company_analysis['total_questions']} interview questions")
        else:
            print(f"❌ Company analysis failed: {company_analysis['error']}")
        
        return prep, insights

async def test_job_market_analyzer():
    """Test the AI-powered job market analyzer"""
    print("\n\n🤖 Testing AI-Powered Job Market Analyzer")
    print("=" * 50)
    
    analyzer = JobMarketAnalyzer()
    
    # Test 1: Comprehensive job market analysis
    print("\n📊 Test 1: Comprehensive job market analysis...")
    analysis = await analyzer.analyze_job_market(
        keywords="software engineer",
        location="San Francisco",
        analysis_depth="comprehensive"
    )
    
    if analysis['success']:
        print(f"✅ Analysis completed successfully")
        print(f"   Jobs analyzed: {analysis['job_data']['total_jobs_analyzed']}")
        print(f"   AI analysis: {'✅' if analysis['ai_analysis'] else '❌'}")
        print(f"   Insights generated: {'✅' if analysis['insights_report'] else '❌'}")
        
        # Show key insights
        if analysis['insights_report']:
            summary = analysis['insights_report'].get('executive_summary', {})
            print(f"   Market summary: {summary.get('market_summary', 'N/A')}")
            print(f"   Top skills: {summary.get('top_skills', [])[:3]}")
    else:
        print(f"❌ Analysis failed: {analysis['error']}")
    
    # Test 2: Interview preparation generation
    print("\n🎯 Test 2: Interview preparation generation...")
    prep = await analyzer.generate_interview_prep(
        job_title="software engineer",
        location="San Francisco",
        prep_type="comprehensive"
    )
    
    if prep['success']:
        print(f"✅ Interview prep generated successfully")
        print(f"   Questions generated: {prep['job_data']['total_questions']}")
        print(f"   Study guide: {'✅' if prep['study_guide'] else '❌'}")
        print(f"   Practice plan: {'✅' if prep['practice_plan'] else '❌'}")
        
        # Show study guide overview
        if prep['study_guide']:
            overview = prep['study_guide'].get('overview', {})
            print(f"   Job title: {overview.get('job_title', 'N/A')}")
            print(f"   Top skills to study: {overview.get('top_skills', [])[:3]}")
    else:
        print(f"❌ Interview prep failed: {prep['error']}")
    
    # Test 3: Company analysis
    print("\n🏢 Test 3: Company analysis with AI...")
    company_analysis = await analyzer.analyze_company_jobs(
        company_name="Apple",
        include_ai_analysis=True
    )
    
    if company_analysis['success']:
        print(f"✅ Company analysis completed")
        print(f"   Company: {company_analysis['company']}")
        print(f"   Jobs found: {company_analysis['job_data']['total_jobs']}")
        print(f"   AI analysis: {'✅' if company_analysis.get('ai_analysis') else '❌'}")
    else:
        print(f"❌ Company analysis failed: {company_analysis['error']}")
    
    return analysis, prep

async def test_mcp_integration():
    """Test the actual MCP integration (requires Cursor)"""
    print("\n\n🔌 Testing MCP Integration")
    print("=" * 50)
    
    print("📝 Note: This test requires running in Cursor with MCP enabled")
    print("   To test MCP integration:")
    print("   1. Open this file in Cursor")
    print("   2. Use the MCP commands directly:")
    print("      - mcp_brightdata-mcp_scrape_as_markdown('https://linkedin.com/jobs/search/?keywords=software%20engineer')")
    print("      - mcp_brightdata-mcp_search_engine_batch([{'query': 'software engineer jobs', 'engine': 'google'}])")
    print("   3. The services will automatically use the scraped data")
    
    # Show how to integrate MCP data
    print("\n💡 Integration example:")
    print("""
    # In Cursor, you can use:
    mcp_brightdata-mcp_scrape_as_markdown('https://www.linkedin.com/jobs/search/?keywords=software%20engineer&f_TPR=r3600')
    
    # Then use the scraped data in your services:
    service = BrightDataMCPService()
    jobs = await service.scrape_linkedin_jobs("software engineer")
    """)

async def save_test_results(results):
    """Save test results to file"""
    try:
        # Create exports directory
        exports_dir = Path("exports")
        exports_dir.mkdir(exist_ok=True)
        
        # Save results
        results_file = exports_dir / "brightdata_integration_test_results.json"
        
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"\n💾 Test results saved to: {results_file}")
        
    except Exception as e:
        print(f"❌ Error saving test results: {e}")

async def main():
    """Main test function"""
    print("🚀 Starting BrightData MCP Integration Tests")
    print("=" * 60)
    
    results = {
        "test_timestamp": "2024-01-01T00:00:00Z",
        "tests": {}
    }
    
    try:
        # Test 1: BrightData Service
        print("\n" + "="*60)
        brightdata_results = await test_brightdata_service()
        results["tests"]["brightdata_service"] = {
            "success": brightdata_results.get('success', False),
            "total_jobs": brightdata_results.get('total_jobs', 0)
        }
        
        # Test 2: Enhanced Crawl4AI
        print("\n" + "="*60)
        prep_results, insights_results = await test_enhanced_crawl4ai()
        results["tests"]["enhanced_crawl4ai"] = {
            "prep_success": prep_results.get('success', False),
            "insights_success": insights_results.get('success', False),
            "total_questions": prep_results.get('total_questions', 0),
            "jobs_analyzed": insights_results.get('total_jobs_analyzed', 0)
        }
        
        # Test 3: Job Market Analyzer
        print("\n" + "="*60)
        analysis_results, prep_analysis_results = await test_job_market_analyzer()
        results["tests"]["job_market_analyzer"] = {
            "analysis_success": analysis_results.get('success', False),
            "prep_success": prep_analysis_results.get('success', False),
            "jobs_analyzed": analysis_results.get('job_data', {}).get('total_jobs_analyzed', 0)
        }
        
        # Test 4: MCP Integration Info
        print("\n" + "="*60)
        await test_mcp_integration()
        results["tests"]["mcp_integration"] = {
            "info_provided": True,
            "requires_cursor": True
        }
        
        # Save results
        await save_test_results(results)
        
        # Summary
        print("\n" + "="*60)
        print("📊 TEST SUMMARY")
        print("="*60)
        
        total_tests = len(results["tests"])
        successful_tests = sum(1 for test in results["tests"].values() if test.get('success', False))
        
        print(f"Total tests: {total_tests}")
        print(f"Successful: {successful_tests}")
        print(f"Failed: {total_tests - successful_tests}")
        
        if successful_tests == total_tests:
            print("🎉 All tests passed! Integration is ready to use.")
        else:
            print("⚠️  Some tests failed. Check the output above for details.")
        
        print("\n💡 Next steps:")
        print("   1. Test MCP integration in Cursor")
        print("   2. Update API endpoints in your FastAPI app")
        print("   3. Test the full workflow end-to-end")
        print("   4. Deploy and monitor performance")
        
    except Exception as e:
        print(f"\n❌ Test suite failed with error: {e}")
        results["error"] = str(e)
        await save_test_results(results)

if __name__ == "__main__":
    asyncio.run(main())
