# Celebrity Twitter Sentiment Analyzer

## Overview
A sophisticated real-time sentiment analysis tool that analyzes public opinion about celebrities on Twitter using the Twitter API v2 and VADER sentiment analysis. The application provides insights into how people genuinely feel about celebrities by focusing on opinion-based tweets while filtering out news and promotional content.

## 🌟 Key Features

### Smart Tweet Filtering
- **Opinion Focus**: Specifically targets tweets containing opinion indicators (think, feel, believe, love, hate)
- **News Filtering**: Automatically filters out news headlines and announcements
- **Content Quality**:
  - Removes URLs while preserving context
  - Filters out retweets to avoid duplicates
  - Ensures minimum content length for meaningful analysis
  - Language filtering (English only)

### Advanced Sentiment Analysis
- **VADER Sentiment Analysis** with custom enhancements:
  - Opinion-aware scoring
  - Confidence metrics for each analysis
  - Three-way classification (Positive, Negative, Neutral)
  - Adjustable sentiment thresholds based on content type

### Interactive Visualization
- **Real-time Analysis Dashboard**
- **Dynamic Charts**: Interactive sentiment distribution visualization
- **Color-coded Results**: Easy-to-interpret sentiment displays
- **Detailed Statistics**: Confidence scores and distribution metrics

## 🎯 Use Cases

1. **Brand Management**
   - Monitor public sentiment during celebrity endorsements
   - Track reputation changes over time
   - Identify potential PR issues early

2. **Entertainment Industry**
   - Analyze audience reception to new releases
   - Monitor fan sentiment during events/tours
   - Track public opinion after media appearances

3. **Media Research**
   - Study public reaction to celebrity news
   - Analyze sentiment trends over time
   - Compare sentiment across different demographics

4. **Crisis Management**
   - Monitor real-time sentiment during controversies
   - Track sentiment recovery after incidents
   - Identify sentiment shift triggers

## 📊 Example Outputs
```
Celebrity: Taylor Swift
Time Period: Last 24 hours
Tweets Analyzed: 100
Results:
- Positive: 45% (High confidence: 0.85)
- Neutral: 30% (Moderate confidence: 0.65)
- Negative: 25% (High confidence: 0.78)
```

## ⚙️ Technical Features

### Time Range Flexibility
- Default ranges (24 hours, 3 days, 7 days)
- Customizable for premium API access
- Rate limit aware with automatic handling

### Smart Opinion Detection
```python
opinion_terms = "(think OR feel OR believe OR love OR hate OR 
                 overrated OR underrated OR amazing OR terrible OR 
                 best OR worst OR good OR bad)"
```

### News Filtering System
```python
news_indicators = [
    'BREAKING:', 'UPDATE:', 'WATCH:', 'NEW:', 'EXCLUSIVE:',
    'REPORT:', 'JUST IN:'
]
```

## 🚀 Installation

1. Clone the repository:
```bash
git clone https://github.com/rabiawaqar06/sentiment-analysis-assignment.git
cd sentiment-analysis-assignment
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up your credentials:
   - Create `.streamlit/secrets.toml`
   - Add your Twitter API token (see template below)

4. Run the application:
```bash
streamlit run app.py
```

## 🔑 API Configuration

Create `.streamlit/secrets.toml`:
```toml
TWITTER_BEARER_TOKEN = "your-twitter-bearer-token-here"
```

## 📋 Requirements
```
streamlit==1.32.2
tweepy==4.14.0
pandas==2.3.1
matplotlib==3.10.3
vaderSentiment==3.3.2
```

## 🛠️ Customization Options

### Adjustable Parameters
- Tweet fetch limit (default: 50, adjustable up to API limits)
- Sentiment thresholds
- Opinion term dictionary
- News filter keywords
- Time ranges (with premium API)

### Sentiment Threshold Examples
```python
# For opinion tweets
if has_opinion:
    positive_threshold = 0.3
    negative_threshold = -0.3
else:
    positive_threshold = 0.5
    negative_threshold = -0.5
```

## 🔒 Security Notes
- Never commit your API credentials
- Use environment variables or secrets management
- Follow Twitter API rate limiting guidelines
- Implement proper error handling

## 🚧 Future Enhancements
- Multi-language support
- Sentiment trend analysis
- Advanced statistical metrics
- Export functionality
- Custom sentiment dictionaries

## ⚠️ Important Notes
1. **API Limits**: Free tier limited to 7-day historical data
2. **Rate Limiting**: Implements automatic rate limit handling
3. **Data Privacy**: Follows Twitter's terms of service
4. **Scalability**: Can be modified for enterprise API access

## 👥 Contributing
Contributions welcome! Please read our contributing guidelines and submit pull requests to our repository.

## 📄 License
This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments
- Twitter API v2 Documentation
- VADER Sentiment Analysis
- Streamlit Community
- Rabia Waqar - Developer

---
**Note**: This project uses the Twitter API v2. For production use, consider upgrading to a premium API access level for increased rate limits and historical data access.
Second Project: stock_sentiment.ipynb 

