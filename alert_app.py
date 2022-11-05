from src.data.tweet_scrapper import TweetScrapper
from src.utils.build_user_df import BuildUserDf
from src.utils.email_users import EmailUsers
import coloredlogs
import logging
import os
import time
from src.utils.users import Users
users = Users()

#--------------logging setup
logger = logging.getLogger(__name__)
coloredlogs.install(level=os.getenv("LOG_LEVEL", "INFO"))
fh = logging.FileHandler('logs/alert_app.log')
logger.addHandler(fh)
fh.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))


#-------------helpers
def get_user_df_and_send_emails(tweet_df):
    builder = BuildUserDf()
    builder.get_and_set_customer_df()
    builder.get_and_set_order_df()
    shop_user_df = builder.build_user_df()
    app_user_df = users.get_users()
    user_df = shop_user_df[['email', 'tor_address', 'km_radius', 'lat', 'lon']].append(
        app_user_df[['email', 'tor_address', 'km_radius', 'lat', 'lon']]
    )
    for ix, row in tweet_df.iterrows():
        if user_df.shape[0] > 0:
            email_users = EmailUsers(user_df)
            sel_users = email_users.filter_to_users_near_the_event(row.lat, row.lon)
            email_users.email_the_right_users(
                sel_users,
                row
            )



#----------main function
def append_to_tables_and_email_users_latest_tweets_every_n_secs(secs=10, log_every=1000):
    logger.info('Starting to listen')
    logger.info(f'Making requests every {secs}s, logging every {log_every}s')
    scrapper = TweetScrapper()
    i = 0
    while True != False:
        if i % log_every == 0:
            logger.info(f'Making request number: {i+1}')
        try: 
            res_df = scrapper.get_tweets_from_last_n_secs("TPSOperations", secs, ops_tweet=True)
            if res_df.shape[0] > 0:
                get_user_df_and_send_emails(res_df)
                scrapper.save_tweetdf_to_db(res_df, "raw_tps_ops_tweets", if_exists="append")
            i += 1
            time.sleep(secs)
        except Exception as err:
            logger.warn(f'Failed with error: {err}')
            logger.info(f'Making request number: {i+1}, sleeping for 1m')
            time.sleep(60)

            try:
                res_df = scrapper.get_tweets_from_last_n_secs(
                    "TPSOperations", 
                    secs + 80, # = 60 + 10 + 10 => pull from the before the 2 sleeps and 10s until now
                    ops_tweet=True
                )
                if res_df.shape[0] > 0:
                    get_user_df_and_send_emails(res_df)
                    scrapper.save_tweetdf_to_db(res_df, "raw_tps_ops_tweets", if_exists="append")
            except Exception as err:
                logger.error(f'Failed with error: {err}')


if __name__ == "__main__":
    append_to_tables_and_email_users_latest_tweets_every_n_secs(secs=10, log_every=10000)