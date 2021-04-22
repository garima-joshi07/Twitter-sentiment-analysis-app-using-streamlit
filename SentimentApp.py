import streamlit as st,pandas as pd, numpy as np, tweepy,json, re,textblob,base64,seaborn as sns,matplotlib,openpyxl,time,tqdm,datetime,os,requests
from textblob import TextBlob
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
import matplotlib.pyplot as plt
matplotlib.use('Agg')
from tweepy import OAuthHandler, OAuthHandler, Stream
from tweepy.streaming import StreamListener
from io import BytesIO
import warnings
warnings.filterwarnings("ignore")

stopwords = set(STOPWORDS)
consumer_key =  "consumer_key",
consumer_secret = "consumer_secret ",
access_token = " access_token",
access_token_secret = "access_token_secret"

def SentimentAnalysisApp():

   

    auth = tweepy.OAuthHandler( consumer_key , consumer_secret )
    auth.set_access_token( access_token , access_token_secret )
    api = tweepy.API(auth)

    st.sidebar.title("Sentiment analysis :") 
    df = pd.DataFrame(columns=["Date","IsVerified","Tweet","Likes","RT",'User_location'])
    
    def get_tweets(QUERY, noOfTweet, startSince, endUntil, i=0):

        for tweet in tweepy.Cursor(api.search, q=QUERY, since=startSince, until=endUntil, lang="en", exclude='retweets').items(noOfTweet):
            df.loc[i,"Date"] = tweet.created_at
            df.loc[i,"IsVerified"] = tweet.user.verified
            df.loc[i,"Tweet"] = tweet.text
            df.loc[i,"Likes"] = tweet.favorite_count
            df.loc[i,"RT"] = tweet.retweet_count
            df.loc[i,"User_location"] = tweet.user.location
            df.to_csv("TweetDataset.csv",index=False)
           
            i = i+1
            
            if i > noOfTweet: break
            else: pass
        
        df.to_csv("new_df.csv", index=True)

    # Function to Clean the Tweet.
    clean_tweet = lambda tweet : ' '.join(re.sub('(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)|([RT])', ' ', tweet.lower()).split())
    
    # Function to analyze Sentiment
    def analyze_sentiment(tweet):
        analysis = TextBlob(tweet)
        return "Positive" if analysis.sentiment.polarity > 0 else "Neutral" if analysis.sentiment.polarity == 0 else "Negative"
    
    #Function to Pre-process data for Wordcloud
    def prepCloud(QUERY_text, QUERY):
        stopwords = set(STOPWORDS)
        stopwords.update(re.split("\s+",str(' '.join(re.sub('([^0-9A-Za-z \t])', ' ', str(QUERY).lower()).split())))) 
        return " ".join([txt for txt in QUERY_text.split() if txt not in stopwords])

    #Function to download data
    def get_binary_file_downloader_html(bin_file, file_label='File'):
        with open(bin_file, 'rb') as f: data = f.read()
        bin_str = base64.b64encode(data).decode()
        return f'<a href="data:application/octet-stream;base64,{bin_str}" download="{os.path.basename(bin_file)}">Download {file_label}</a>'
    
    # Collect Input from user :   
    query_string = str(st.sidebar.text_input("Enter the topic you are interested in:").split(","))[1:-1].replace("'", '"')
    QUERY = query_string.replace(',', ' OR ')
    noOfTweet = st.sidebar.selectbox('Select number of tweets to analyze:', [200, 300, 400, 500, 1000, 1500])
    today = datetime.date.today()
    #tomorrow = datetime.date.today()
    tomorrow = today + datetime.timedelta(days=1)
    startSince = st.sidebar.date_input('Start date', today)
    endUntil = st.sidebar.date_input('End date', tomorrow)
    #start_time = st.sidebar.time_input("Start time",datetime.time())
    #end_time = st.sidebar.time_input("End time is",datetime.time())

    if st.sidebar.button("Analyze Tweets about {}".format(QUERY)) and len(QUERY) > 0:
        if startSince <= endUntil:
            st.sidebar.success('Start date: `%s`\n\nEnd date:`%s`' % (startSince, endUntil))
        #else: st.sidebar.error('Error: End date must be greater than or equal to start date.')

            #if start_time <= end_time: st.sidebar.success('Start time: `%s`\n\nEnd time:`%s`' % (start_time, end_time))
        else: st.sidebar.error('Error: End date must be greater than or equal to start date.')

        with st.spinner("Please wait, Tweets are being extracted"): get_tweets(QUERY,noOfTweet, startSince,endUntil)

        st.sidebar.success('Tweets have been Extracted !!!!') 
        stop = st.sidebar.button("Reset")
    
        #Clean tweets
        df['clean_tweet'] = df['Tweet'].apply(lambda x : clean_tweet(x))
    
        df["Sentiment"] = df["Tweet"].apply(lambda x : analyze_sentiment(x))
        df.to_csv("tweet_data.csv", index=True)
    
        #Summary of the Tweets
        st.write("Total Tweets Extracted for Topic '{}' are : {}".format(QUERY,len(df.Tweet)))
        st.write("Total Positive Tweets are : {}".format(len(df[df["Sentiment"] == "Positive"])))
        st.write("Total Negative Tweets are : {}".format(len(df[df["Sentiment"] == "Negative"])))
        st.write("Total Neutral Tweets are : {}".format(len(df[df["Sentiment"] == "Neutral"])))

        a = len(df[df["Sentiment"] == "Positive"])
        b = len(df[df["Sentiment"] == "Negative"])
        c = len(df[df["Sentiment"] == "Neutral"])

        if a == 0 or b == 0 or c == 0: st.sidebar.error('Error: Required tweets not found, change either input query or date')
        else: pass
        
        st.success("Below is the Extracted Data :")
        st.write(df.head(50))
        st.markdown(get_binary_file_downloader_html('tweet_data.csv', 'Text'), unsafe_allow_html=True)
        st.success("Analysing Tweets about {}".format(QUERY))
        st.success("Generating Pie Chart:")
        plt.pie(np.array([a, b, c]), shadow=False,labels=["Positive","Negative","Neutral"], autopct='%1.2f%%', startangle=140, radius = 1.3,textprops = {"fontsize":15})
        plt.savefig('pie_chart.jpg')
        image1 = 'pie_chart.jpg'
        
        with st.beta_container():
            for col in st.beta_columns(1):
                col.image(image1, use_column_width=True)
        
        st.markdown(get_binary_file_downloader_html('pie_chart.jpg', 'Pie Chart for Different Sentiments'), unsafe_allow_html=True)
    
        # Create a Worlcloud
        st.success("Generating a WordCloud for all things said about {}".format(QUERY))
        #wordcloud = WordCloud(width=1600, height=800, background_color = "white", min_font_size=7, max_words=300, relative_scaling=0.5).generate(prepCloud(" ".join(review for review in df.clean_tweet), QUERY))
        wordcloud = WordCloud(width=1600, height=800, background_color = "white",min_font_size=7, stopwords=stopwords).generate(prepCloud(" ".join(review for review in df.clean_tweet), QUERY))          
        plt.figure( figsize=(20, 10), facecolor='k')
        plt.axis("off")
        plt.tight_layout(pad=0)
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.savefig('word_cloud_alltweets.jpg')
        image2 = 'word_cloud_alltweets.jpg'
        
        with st.beta_container():
            for col in st.beta_columns(1):
                col.image(image2, use_column_width=True)
                
        st.markdown(get_binary_file_downloader_html('word_cloud_alltweets.jpg', 'WordCloud for all tweets'), unsafe_allow_html=True)
    
        #Wordcloud for Positive tweets only
        st.success("Generating A WordCloud for all Positive Tweets about {}".format(QUERY))
        text_positive = " ".join(review for review in df[df["Sentiment"]=="Positive"].clean_tweet)
        text_new_positive = prepCloud(text_positive,QUERY)
        wordcloud = WordCloud(width=1600, height=800, background_color = "white",stopwords=stopwords).generate(text_new_positive)
        plt.figure(figsize=(20,10), facecolor='k')
        plt.axis("off")
        plt.tight_layout(pad=0)
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.savefig('word_cloud_PositiveTweets.jpg')
        image3='word_cloud_PositiveTweets.jpg'
        
        with st.beta_container():
            for col in st.beta_columns(1):
                col.image(image3, use_column_width=True)
        
        st.markdown(get_binary_file_downloader_html('word_cloud_PositiveTweets.jpg', 'WordCloud for Positive tweets'), unsafe_allow_html=True)
        
        #Wordcloud for Negative tweets only       
    
        st.success("Generating A WordCloud for all Negative Tweets about {}".format(QUERY))
        text_negative = " ".join(review for review in df[df["Sentiment"]=="Negative"].clean_tweet)
        text_new_negative = prepCloud(text_negative,QUERY)
        wordcloud = WordCloud(width=1600, height=800,  background_color = "white",stopwords=stopwords).generate(text_new_negative)          
        plt.figure(figsize = (20, 10), facecolor = 'k')
        plt.axis("off")
        plt.tight_layout(pad=0)
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.savefig('word_cloud_NegativeTweets.jpg')
        image4='word_cloud_NegativeTweets.jpg'
        
        with st.beta_container():
            for col in st.beta_columns(1):
                col.image(image4, use_column_width=True)
        
        st.markdown(get_binary_file_downloader_html('word_cloud_NegativeTweets.jpg', 'WordCloud for negative tweets'), unsafe_allow_html=True)
    
        #Wordcloud for Neutral tweets only       
        st.success("Generating A WordCloud for all Neutral Tweets about {}".format(QUERY))
        text_neutral = " ".join(review for review in df[df["Sentiment"]=="Neutral"].clean_tweet)
        text_new_neutral = prepCloud(text_neutral,QUERY)
        wordcloud = WordCloud(width=1600, height=800, background_color = "white",stopwords=stopwords).generate(text_new_neutral)          
        plt.figure( figsize=(20,10), facecolor='k')
        plt.axis("off")
        plt.tight_layout(pad=0)
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.savefig('word_cloud_NeutralTweets.jpg')
        image5 = 'word_cloud_NeutralTweets.jpg'
        
        with st.beta_container():
            for col in st.beta_columns(1):
                col.image(image5, use_column_width=True)
        
        st.markdown(get_binary_file_downloader_html('word_cloud_NeutralTweets.jpg', 'WordCloud for neutral tweets'), unsafe_allow_html=True)

if __name__ == '__main__':
    SentimentAnalysisApp()