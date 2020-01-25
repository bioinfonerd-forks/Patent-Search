from utils.common import ConfigUtil

config = ConfigUtil()


class User():

    def __init__(self, email, password):
        self.email = email
        self.password = password


class OrderInfo():

    def __init__(self):

        shop_region = config.load_value('review', 'shop_region', 'US')
        if shop_region == 'US':
            standard_time_zone = 'PST'
        else:
            standard_time_zone = 'MET'
        self.order_id = None
        self.order_date = None
        self.buyer_name = None
        self.purchase_date = None
        self.standard_time_zone = standard_time_zone
        self.buyer_time_zone = None
        self.customer_option = None
        self.ship_address = None
        self.ship_state = None
        self.ship_region = None
        self.ship_abbreviation = None
        self.ship_city = None
        self.ship_date = None
        self.ship_service = None
        self.ship_zip_code = None
        self.fulfillment = None
        self.sales_channel = None
        self.latest_request_review_status = None
        self.latest_request_review_datetime = None
        self.buyer_rating = None
        self.buyer_comment = None
        self.buyer_feedback = None
        self.refund = None


if __name__ == '__main__':
    pass
    # standard_time_zone = config.load_value('order', 'date_range_start', 'PST')
    # print(standard_time_zone)
    # order_info = OrderInfo()
    # print(order_info.standard_time_zone)



