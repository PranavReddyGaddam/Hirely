# 🔗 Source URL Feature for Interview Questions

## ✅ **What's Added**

Every interview question now includes the **source URL** where it was found, allowing you to:

- ✅ **Verify Questions**: Click the link to see the original post
- ✅ **Read Full Context**: See the complete interview experience
- ✅ **Check Recency**: Verify when the interview took place
- ✅ **Understand Difficulty**: Read the full context of the question

## 📊 **Output Format**

### **Console Display**
```
📚 Real Interview Questions (from actual experiences):
   1. How would you design a URL shortener like bit.ly?
      Source: LeetCode Discuss | Company: Google
      Category: Technical | Difficulty: Hard
      🔗 Source URL: https://leetcode.com/discuss/interview-question/123456/google-l4-system-design

   2. Tell me about a time you had to debug a production issue.
      Source: Glassdoor | Company: Google  
      Category: Behavioral | Difficulty: Medium
      🔗 Source URL: https://www.glassdoor.com/Interview/Google-Software-Engineer-Interview-Questions-EI_IE9079.0,6_KO7,25.htm
```

### **JSON Output**
```json
{
  "real_questions": [
    {
      "question": "How would you design a URL shortener like bit.ly?",
      "source": "LeetCode Discuss",
      "source_url": "https://leetcode.com/discuss/interview-question/123456/google-l4-system-design",
      "company": "Google",
      "position": "Software Engineer",
      "experience_type": "Real Interview Experience",
      "difficulty": "Hard",
      "category": "Technical"
    }
  ]
}
```

## 🎯 **Benefits**

### **For Verification**
- ✅ **Click to Verify**: Direct links to original posts
- ✅ **Read Full Context**: Complete interview experience
- ✅ **Check Authenticity**: Verify the question is real
- ✅ **See Comments**: Read other candidates' experiences

### **For Preparation**
- ✅ **Understand Context**: See the full interview scenario
- ✅ **Read Solutions**: Find answers and discussions
- ✅ **Check Difficulty**: Understand the actual difficulty level
- ✅ **Learn Patterns**: See what questions are commonly asked

### **For Research**
- ✅ **Track Sources**: Know which websites have the best content
- ✅ **Find More**: Discover related interview experiences
- ✅ **Verify Recency**: Check when the interview took place
- ✅ **Build Database**: Collect verified interview questions

## 🔍 **Source Types**

### **1. LeetCode Discuss**
- **URL Format**: `https://leetcode.com/discuss/interview-question/{id}/`
- **Content**: Technical questions with solutions
- **Value**: High-quality technical content

### **2. Glassdoor Interviews**
- **URL Format**: `https://www.glassdoor.com/Interview/{company}-{position}-Interview-Questions.htm`
- **Content**: Interview experiences and questions
- **Value**: Company-specific insights

### **3. Indeed Reviews**
- **URL Format**: `https://www.indeed.com/cmp/{company}/reviews`
- **Content**: Interview feedback and experiences
- **Value**: Process insights and questions

### **4. Blind (TeamBlind)**
- **URL Format**: `https://www.teamblind.com/t/{topic}`
- **Content**: Anonymous interview experiences
- **Value**: Honest, unfiltered experiences

## 🚀 **Usage Example**

```bash
cd backend
source venv/bin/activate
python test_job_to_questions.py

# Enter job posting URL
🔗 Job Posting URL: https://linkedin.com/jobs/view/123456

# Output includes source URLs
📚 Real Interview Questions (from actual experiences):
   1. How would you design a distributed cache?
      Source: LeetCode Discuss | Company: Google
      Category: Technical | Difficulty: Hard
      🔗 Source URL: https://leetcode.com/discuss/interview-question/789012/google-l5-system-design
```

## 📋 **JSON File Output**

The saved JSON file includes all source URLs:

```json
{
  "real_questions": [
    {
      "question": "How would you design a distributed cache?",
      "source": "LeetCode Discuss",
      "source_url": "https://leetcode.com/discuss/interview-question/789012/google-l5-system-design",
      "company": "Google",
      "position": "Software Engineer",
      "experience_type": "Real Interview Experience",
      "difficulty": "Hard",
      "category": "Technical"
    }
  ],
  "generated_questions": [
    {
      "question": "Explain the difference between a hash table and a binary tree.",
      "category": "Technical",
      "difficulty": "Medium",
      "skill_focus": "Data Structures"
    }
  ]
}
```

## 🎉 **Result**

**Now you can:**
- ✅ **Click any question** to see the original source
- ✅ **Read full context** of the interview experience
- ✅ **Verify authenticity** of each question
- ✅ **Build a database** of verified interview questions
- ✅ **Track sources** for future reference

This makes the tool much more valuable for interview preparation! 🚀
