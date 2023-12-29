class Trailer():
    def __init__(self, id=None, req_power=None, price=None, dilivery_time=None, req_efficiency=None):
        self.id = id
        self.req_power = req_power
        self.req_efficiency = req_efficiency
        self.price = price
        self.dilivery_time = dilivery_time
        self.rating = 0
        self.dilivery_time_rating = 1
        self.price_rating = 1
        self.efficiency_rating = 1
        self.power_rating = 1

        self.base_dilivery_time_rating = 0.4
        self.base_price_rating = 0.25
        self.base_efficiency_rating = 0
        # self.base_power_rating = 0.1
        self.base_power_rating = 0


    def SetRating(self):
        rating = self.dilivery_time_rating
        rating += self.price_rating
        rating += self.efficiency_rating
        rating += self.power_rating
        self.rating = rating

    def AddtractorRating(self, tractor_dilivery_time_rating, tractor_price_rating, tractor_efficiency_rating, tractor_power_rating):
        self.dilivery_time_rating = (1-self.base_dilivery_time_rating) * \
            tractor_dilivery_time_rating + \
            self.base_dilivery_time_rating * self.dilivery_time_rating
        self.price_rating = (1-self.base_price_rating) * \
            tractor_price_rating + self.base_price_rating * self.price_rating
        self.efficiency_rating = (1-self.base_efficiency_rating) * \
            tractor_efficiency_rating + self.base_efficiency_rating * self.efficiency_rating
        self.power_rating = (1-self.base_power_rating) * \
            tractor_power_rating + self.base_power_rating * self.power_rating

    def SetPriceRating(self, max_price, min_price):
        if max_price != min_price:
            self.price_rating = (max_price-self.price)/(max_price-min_price)

    def SetPowerRating(self, max_req_power, min_req_power):
        if max_req_power != min_req_power:
            self.power_rating = 1 - \
                (max_req_power-self.req_power)/(max_req_power-min_req_power)

    def SetEfficiencyRating(self):
        self.efficiency_rating = 1

    def SetDiliveryTimeRating(self, max_dilivery_time, min_dilivery_time):
        if self.dilivery_time and max_dilivery_time != min_dilivery_time:
            self.dilivery_time_rating = (max_dilivery_time-self.dilivery_time) / \
                (max_dilivery_time-min_dilivery_time)

    def ToAnswer(self, is_markers_required = True):
        if is_markers_required:
            ans = {
                "id": self.id,
                "markers": [
                    {
                        "name": "efficiency",
                        "value": int(100*self.efficiency_rating)/10,
                    },
                    {
                        "name": "power",
                        "value": int(100*self.power_rating)/10,
                    },
                    {
                        "name": "price",
                        "value": int(100*self.price_rating)/10,
                    },
                    {
                        "name": "distance",
                        "value": int(100*self.dilivery_time_rating)/10,
                    },
                ]
            }
        else:
            
            ans = {
                "id": self.id,
            }
        return ans

    def getMarkers(self):
        markers = {
            "efficiency": self.efficiency_rating,
            "power": self.power_rating,
            "price": self.price_rating,
            "distance": self.dilivery_time_rating,
        }
        return markers
