#!/usr/bin/env python3
"""
Example usage of BrightData MCP integration with Crawl4AI
This script demonstrates the key features of the integrated system.
"""

import asyncio
import json
from pathlib import Path

# Add the app directory to the Python path
import sys
sys.path.append(str(Path(__file__).parent / "app"))

from app.services.crawl4ai_service import Crawl4AIService
from app.services.job_market_analyzer import JobMarketAnalyzer

async def example_job_scraping():
    """Example: Basic job scraping and analysis"""
    print("🔍 Example 1: Job Scraping and Analysis")
    print("=" * 50)
    
    async with Crawl4AIService() as service:
        # Scrape jobs for interview preparation
        print("📚 Scraping jobs for interview prep...")
        prep = await service.scrape_jobs_for_interview_prep(
            job_title="software engineer",
            location="San Francisco",
            max_jobs=10
        )
        
        if prep['success']:
            print(f"✅ Found {prep['total_jobs']} jobs")
            print(f"✅ Generated {prep['total_questions']} interview questions")
            print(f"✅ Top skills: {list(prep['skills_analysis'].keys())[:5]}")
            
            # Show sample questions
            print("\n📝 Sample interview questions:")
            for i, q in enumerate(prep['interview_questions'][:3], 1):
                print(f"   {i}. {q['question']}")
        else:
            print(f"❌ Failed: {prep['error']}")

async def example_market_analysis():
    """Example: Comprehensive market analysis"""
    print("\n\n📊 Example 2: Market Analysis")
    print("=" * 50)
    
    analyzer = JobMarketAnalyzer()
    
    # Perform market analysis
    print("🤖 Analyzing job market...")
    analysis = await analyzer.analyze_job_market(
        keywords="software engineer",
        location="San Francisco",
        analysis_depth="comprehensive"
    )
    
    if analysis['success']:
        print(f"✅ Analyzed {analysis['job_data']['total_jobs_analyzed']} jobs")
        
        # Show insights
        insights = analysis['insights_report']
        print(f"✅ Market summary: {insights['executive_summary']['market_summary']}")
        print(f"✅ Top skills: {insights['executive_summary']['top_skills'][:3]}")
        print(f"✅ Recommendations: {len(insights['recommendations'])} provided")
    else:
        print(f"❌ Analysis failed: {analysis['error']}")

async def example_company_analysis():
    """Example: Company-specific analysis"""
    print("\n\n🏢 Example 3: Company Analysis")
    print("=" * 50)
    
    analyzer = JobMarketAnalyzer()
    
    # Analyze specific company
    print("🔍 Analyzing company jobs...")
    company_analysis = await analyzer.analyze_company_jobs(
        company_name="Google",
        include_ai_analysis=True
    )
    
    if company_analysis['success']:
        print(f"✅ Analyzed {company_analysis['job_data']['total_jobs']} jobs from {company_analysis['company']}")
        
        if company_analysis.get('ai_analysis'):
            print("✅ AI analysis completed")
        else:
            print("⚠️  AI analysis not available")
    else:
        print(f"❌ Company analysis failed: {company_analysis['error']}")

async def example_interview_prep():
    """Example: Complete interview preparation"""
    print("\n\n🎯 Example 4: Complete Interview Preparation")
    print("=" * 50)
    
    analyzer = JobMarketAnalyzer()
    
    # Generate comprehensive interview prep
    print("📖 Generating interview preparation...")
    prep = await analyzer.generate_interview_prep(
        job_title="software engineer",
        location="San Francisco",
        prep_type="comprehensive"
    )
    
    if prep['success']:
        print(f"✅ Generated {prep['job_data']['total_questions']} questions")
        
        # Show study guide overview
        study_guide = prep['study_guide']
        overview = study_guide['overview']
        print(f"✅ Job title: {overview['job_title']}")
        print(f"✅ Skills to study: {overview['top_skills'][:5]}")
        
        # Show practice plan
        practice_plan = prep['practice_plan']
        print(f"✅ Weekly schedule: {len(practice_plan['weekly_schedule'])} weeks planned")
        print(f"✅ Daily practice: {practice_plan['daily_practice']}")
        print(f"✅ Goals: {len(practice_plan['goals'])} goals set")
    else:
        print(f"❌ Interview prep failed: {prep['error']}")

async def example_mcp_usage():
    """Example: How to use MCP commands in Cursor"""
    print("\n\n🔌 Example 5: MCP Usage in Cursor")
    print("=" * 50)
    
    print("📝 To use MCP commands in Cursor, run these commands:")
    print()
    print("1. Scrape LinkedIn jobs:")
    print("   mcp_brightdata-mcp_scrape_as_markdown('https://www.linkedin.com/jobs/search/?keywords=software%20engineer&f_TPR=r3600')")
    print()
    print("2. Search multiple queries:")
    print("   mcp_brightdata-mcp_search_engine_batch([")
    print("     {'query': 'software engineer jobs', 'engine': 'google'},")
    print("     {'query': 'data scientist jobs', 'engine': 'google'}")
    print("   ])")
    print()
    print("3. Scrape multiple URLs:")
    print("   mcp_brightdata-mcp_scrape_batch([")
    print("     'https://www.linkedin.com/jobs/search/?keywords=software%20engineer',")
    print("     'https://www.linkedin.com/jobs/search/?keywords=data%20scientist'")
    print("   ])")
    print()
    print("💡 The services will automatically use the scraped data from MCP commands!")

async def save_examples():
    """Save example results to file"""
    print("\n\n💾 Saving Example Results")
    print("=" * 50)
    
    try:
        # Create examples directory
        examples_dir = Path("examples")
        examples_dir.mkdir(exist_ok=True)
        
        # Example data
        example_data = {
            "timestamp": "2024-01-01T00:00:00Z",
            "examples": {
                "job_scraping": {
                    "description": "Basic job scraping and interview question generation",
                    "endpoint": "POST /api/v1/job-analysis/scrape-jobs",
                    "service": "Crawl4AIService.scrape_jobs_for_interview_prep()"
                },
                "market_analysis": {
                    "description": "Comprehensive job market analysis with AI insights",
                    "endpoint": "POST /api/v1/job-analysis/analyze-job-market",
                    "service": "JobMarketAnalyzer.analyze_job_market()"
                },
                "company_analysis": {
                    "description": "Company-specific job analysis and insights",
                    "endpoint": "POST /api/v1/job-analysis/scrape-company-jobs",
                    "service": "JobMarketAnalyzer.analyze_company_jobs()"
                },
                "interview_prep": {
                    "description": "Complete interview preparation with study guide",
                    "endpoint": "POST /api/v1/job-analysis/generate-interview-prep",
                    "service": "JobMarketAnalyzer.generate_interview_prep()"
                }
            },
            "mcp_commands": [
                "mcp_brightdata-mcp_scrape_as_markdown()",
                "mcp_brightdata-mcp_search_engine_batch()",
                "mcp_brightdata-mcp_scrape_batch()"
            ]
        }
        
        # Save to file
        examples_file = examples_dir / "brightdata_integration_examples.json"
        with open(examples_file, 'w', encoding='utf-8') as f:
            json.dump(example_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Examples saved to: {examples_file}")
        
    except Exception as e:
        print(f"❌ Error saving examples: {e}")

async def main():
    """Run all examples"""
    print("🚀 BrightData MCP Integration Examples")
    print("=" * 60)
    
    try:
        # Run examples
        await example_job_scraping()
        await example_market_analysis()
        await example_company_analysis()
        await example_interview_prep()
        await example_mcp_usage()
        await save_examples()
        
        print("\n" + "=" * 60)
        print("✅ All examples completed successfully!")
        print("\n💡 Next steps:")
        print("   1. Try the MCP commands in Cursor")
        print("   2. Test the API endpoints")
        print("   3. Integrate with your frontend")
        print("   4. Customize for your specific needs")
        
    except Exception as e:
        print(f"\n❌ Examples failed with error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
