import streamlit as st
import tweepy
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import re
import time
import os
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# Page config
st.set_page_config(
    page_title="Celebrity Twitter Sentiment",
    page_icon="🐦",
    layout="wide"
)

def setup_twitter_client():
    """Initialize and return the Twitter API client."""
    try:
        bearer_token = st.secrets["TWITTER_BEARER_TOKEN"]
        if not bearer_token:
            st.error("Twitter API token not found. Please check your .streamlit/secrets.toml file.")
            return None
        client = tweepy.Client(bearer_token=bearer_token)
        return client
    except Exception as e:
        st.error(f"Error initializing Twitter client: {str(e)}")
        return None

def clean_text(text):
    """
    Clean tweet text while preserving sentiment indicators.
    Filter out news-style content.
    """
    # Skip news headlines and announcements
    if any(text.strip().startswith(prefix) for prefix in [
        'BREAKING:', 'Breaking:', 'UPDATE:', 'WATCH:', 'NEW:', 'EXCLUSIVE:',
        'REPORT:', 'Report:', 'JUST IN:', 'Just in:'
    ]):
        return ""
        
    # Remove URLs but keep mentions and hashtags
    text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
    
    # Remove extra whitespace
    text = ' '.join(text.split())
    
    # Skip if text is too short after cleaning
    if len(text.split()) < 3:
        return ""
        
    return text

def analyze_sentiment(text):
    """
    Analyze sentiment using VADER with focus on opinion expressions.
    """
    if not text:
        return {
            'sentiment': 'neutral',
            'confidence': 0.0,
            'compound': 0.0
        }
    
    analyzer = SentimentIntensityAnalyzer()
    scores = analyzer.polarity_scores(text)
    compound = scores['compound']
    
    # Check for opinion indicators
    opinion_words = [
        'think', 'feel', 'believe', 'opinion', 'love', 'hate',
        'amazing', 'terrible', 'worst', 'best', 'overrated',
        'underrated', 'deserves', 'should', 'would', 'could',
        'great', 'awful', 'bad', 'good', 'fantastic', 'horrible'
    ]
    
    has_opinion = any(word in text.lower() for word in opinion_words)
    
    # Adjust thresholds based on opinion presence
    if has_opinion:
        if compound >= 0.3:
            sentiment = 'positive'
            confidence = min(abs(compound) * 1.2, 1.0)  # Boost confidence for clear opinions
        elif compound <= -0.3:
            sentiment = 'negative'
            confidence = min(abs(compound) * 1.2, 1.0)
        else:
            sentiment = 'neutral'
            confidence = 1 - abs(compound)
    else:
        # More conservative thresholds for non-opinion text
        if compound >= 0.5:
            sentiment = 'positive'
            confidence = min(abs(compound), 1.0)
        elif compound <= -0.5:
            sentiment = 'negative'
            confidence = min(abs(compound), 1.0)
        else:
            sentiment = 'neutral'
            confidence = 1 - abs(compound)
    
    return {
        'sentiment': sentiment,
        'confidence': round(confidence, 2),
        'compound': round(compound, 2)
    }

def plot_sentiment(df):
    """
    Create a sentiment distribution bar chart using Matplotlib.
    
    Args:
        df (pd.DataFrame): DataFrame with sentiment analysis results
    """
    # Clear any existing plots
    plt.clf()
    
    # Extract sentiment values from the nested dictionary
    df['sentiment_label'] = df['sentiment'].apply(lambda x: x['sentiment'] if isinstance(x, dict) else 'neutral')
    
    # Calculate sentiment counts and percentages
    sentiment_counts = df['sentiment_label'].value_counts()
    total = len(df)
    percentages = (sentiment_counts / total * 100).round(1)
    
    # Set up colors for each sentiment
    colors = {
        'positive': '#2ecc71',
        'neutral': '#95a5a6',
        'negative': '#e74c3c'
    }
    
    # Create figure and axis with white background
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.set_facecolor('white')
    fig.patch.set_facecolor('white')
    
    # Create bars with safe color mapping
    x_pos = range(len(sentiment_counts))
    bars = ax.bar(x_pos, sentiment_counts.values, 
                 color=[colors.get(sent, '#95a5a6') for sent in sentiment_counts.index])
    
    # Customize the plot
    ax.set_title('Sentiment Distribution', pad=20, fontsize=14, fontweight='bold')
    ax.set_xlabel('Sentiment', labelpad=10, fontsize=12)
    ax.set_ylabel('Number of Tweets', labelpad=10, fontsize=12)
    
    # Set x-axis labels
    ax.set_xticks(x_pos)
    ax.set_xticklabels(sentiment_counts.index, fontsize=11)
    
    # Add grid for better readability
    ax.yaxis.grid(True, linestyle='--', alpha=0.7)
    ax.set_axisbelow(True)  # Put grid behind bars
    
    # Add value labels on top of bars
    for i, bar in enumerate(bars):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, height,
                f'{int(height)}\n({percentages[sentiment_counts.index[i]]}%)',
                ha='center', va='bottom',
                fontsize=10)
    
    # Remove top and right spines
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    # Adjust layout
    plt.tight_layout()
    
    return fig

def fetch_tweets(client, query, start_time, end_time, max_tweets=50):
    """
    Fetch tweets mentioning the celebrity within the date range.
    Focus on opinion tweets rather than news headlines.
    """
    tweets = []
    
    try:
        # Construct query to focus on opinion tweets
        opinion_terms = "(think OR feel OR believe OR love OR hate OR overrated OR underrated OR amazing OR terrible OR best OR worst OR good OR bad)"
        filtered_query = f'"{query}" {opinion_terms} -is:retweet -has:links lang:en'
        
        # Use pagination to get tweets
        for response in tweepy.Paginator(
            client.search_recent_tweets,
            query=filtered_query,
            start_time=start_time,
            end_time=end_time,
            max_results=10,
            tweet_fields=['created_at', 'text'],
            limit=(max_tweets + 9) // 10
        ):
            if response.data:
                tweets.extend([{
                    'created_at': tweet.created_at,
                    'text': tweet.text
                } for tweet in response.data])
                
                if len(tweets) >= max_tweets:
                    tweets = tweets[:max_tweets]
                    break
            
            time.sleep(2)  # Be nice to the API
            
    except tweepy.TooManyRequests:
        st.warning("Rate limit reached. Please wait a few minutes and try again.")
    except Exception as e:
        st.error(f"Error fetching tweets: {str(e)}")
        
    return tweets

def main():
    st.title("Celebrity Twitter Sentiment 🐦")
    st.write("Analyze public sentiment about celebrities on Twitter (Last 7 days)")
    
    try:
        # Initialize Twitter client
        client = setup_twitter_client()
        if not client:
            return
        
        # User inputs
        celebrity_name = st.text_input("Celebrity Name", placeholder="e.g., Taylor Swift")
        
        # Date range selection with max 7 days for free API
        end_time = datetime.utcnow() - timedelta(minutes=1)  # Fixed datetime call
        date_option = st.radio(
            "Select Time Period",
            ["Last 24 hours", "Last 3 days", "Last 7 days"]
        )
        
        if date_option == "Last 24 hours":
            start_time = end_time - timedelta(hours=24)
        elif date_option == "Last 3 days":
            start_time = end_time - timedelta(days=3)
        else:  # Last 7 days
            start_time = end_time - timedelta(days=7)

        max_tweets = st.slider("Maximum number of tweets to analyze", 10, 100, 50)
        
        if st.button("Run Analysis"):
            if not celebrity_name:
                st.warning("Please enter a celebrity name.")
                return
                
            with st.spinner("Fetching tweets..."):
                tweets = fetch_tweets(
                    client,
                    celebrity_name.strip(),  # Remove any extra whitespace
                    start_time,
                    end_time,
                    max_tweets
                )
                
            if not tweets:
                st.warning(f"No tweets found mentioning {celebrity_name} in the selected date range.")
                return
                
            # Create DataFrame and analyze sentiment
            with st.spinner("Analyzing sentiment..."):
                df = pd.DataFrame(tweets)
                if df.empty:
                    st.warning("No valid tweets to analyze.")
                    return
                    
                df['cleaned_text'] = df['text'].apply(clean_text)
                
                # Remove rows with empty cleaned text
                df = df[df['cleaned_text'].str.len() > 0].reset_index(drop=True)
                
                if df.empty:
                    st.warning("No valid tweets remained after cleaning.")
                    return
                
                # Apply sentiment analysis and extract components
                sentiment_results = df['cleaned_text'].apply(analyze_sentiment)
                df['sentiment'] = sentiment_results
                df['sentiment_label'] = sentiment_results.apply(lambda x: x['sentiment'])
                df['confidence'] = sentiment_results.apply(lambda x: x['confidence'])
                
            # Display results
            st.subheader("Analysis Results")
            st.write(f"Analyzed {len(df)} tweets about {celebrity_name} from {start_time.strftime('%Y-%m-%d %H:%M')} to {end_time.strftime('%Y-%m-%d %H:%M')}")
            
            # Show sentiment distribution
            try:
                fig = plot_sentiment(df)
                if fig:
                    st.pyplot(fig)
                else:
                    st.warning("Could not generate sentiment plot.")
            except Exception as e:
                st.error(f"Error generating plot: {str(e)}")
            
            # Display sample tweets with analysis
            if len(df) > 0:
                st.subheader("Sample Tweets with Analysis")
                sample_size = min(5, len(df))
                sample_df = df.sample(sample_size)[['created_at', 'text', 'sentiment_label', 'confidence']]
                
                # Format the dataframe
                def format_row(row):
                    color = '#2ecc7133' if row['sentiment_label'] == 'positive' else '#e74c3c33' if row['sentiment_label'] == 'negative' else '#95a5a633'
                    return [f'background-color: {color}'] * len(row)
                
                st.dataframe(
                    sample_df.style.apply(format_row, axis=1),
                    use_container_width=True
                )
                
                # Display analysis statistics
                st.subheader("Analysis Statistics")
                col1, col2 = st.columns(2)
                
                with col1:
                    avg_confidence = df['confidence'].mean()
                    st.metric("Average Confidence", f"{avg_confidence:.2f}")
                with col2:
                    most_common = df['sentiment_label'].mode()[0]
                    st.metric("Most Common Sentiment", most_common)
                    
                # Display sentiment percentages
                sentiment_counts = df['sentiment_label'].value_counts()
                total = len(df)
                st.write("\nSentiment Distribution:")
                for sentiment, count in sentiment_counts.items():
                    percentage = (count / total * 100)
                    st.write(f"{sentiment.title()}: {count} tweets ({percentage:.1f}%)")
                    
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        st.write("Please try again or contact support if the error persists.")


if __name__ == "__main__":
    main() 