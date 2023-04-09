import requests
import base64
import json

class MissingParameterError(Exception):
    """
    Missing parameter error
    """
    pass

class AuthError(Exception):
    """
    Authentication error
    """
    pass



class UnknownError(Exception):
    """
    Unknown error
    """
    pass

class Api(object):

    def __init__(self, proxies=None, certificate=None, user_agent=None, contract_id=None, code=None,loyality_code=None) -> None:
        self.session = requests.session()

        if contract_id and code and loyality_code:
            self.contract_id = contract_id
            self.loyal_code = loyality_code
            
            tempStr = str(contract_id) + ":" + str(code)
            sample_string_bytes = tempStr.encode("ascii")
            base64_bytes = base64.b64encode(sample_string_bytes)
            self.basicAuthToken = base64_bytes.decode("ascii")
        else:
            raise MissingParameterError("Missing contract_id and code")

        if proxies:
            self.session.proxies.update(proxies)
        if certificate:
            self.session.verify = certificate

        self.session.headers = {
            'Accept-Charset': 'UTF-8',
            'X-CGD-APP-Version': '3.7.0',
            'X-CGD-APP-Name': 'APP_CAIXADIRECTA',
            'X-CGD-APP-LANGUAGE': 'pt-PT',
            'X-CGD-APP-Device': '',
            'User-Agent': '',
            'Host': 'app.cgd.pt',
            'Connection': 'close',
            'Accept-Encoding': 'gzip, deflate',
        }
        if user_agent:
            self.session.headers.update({"User-Agent", user_agent})
        pass

    def login(self):
        url = f"https://app.cgd.pt/pceApi/rest/v1/system/security/authentications/basic?u={self.contract_id}&includeAccountsInResponse=false"

        headersTemp = self.session.headers.copy()
        headersTemp.update({
            'X-CGD-APP-LOYALTY-CODE': self.loyal_code,
            'Authorization': "Basic "+self.basicAuthToken,
        })
        response = self.session.post(url, headers=headersTemp, json={})
        if(response.status_code != 200):
            raise AuthError();

    def mbway_create_card(self,cardName,amount):
        self.get_main_card()
        url = "https://app.cgd.pt/pceApi/rest/v1/business/cards/mbnet/card/simulations"
        
        payload = "{\"operationId\":null,\"operationName\":\"\",\"operationEmail\":null,\"forceDuplicateOperation\":false,\"scheduling\":{\"startDate\":\"\",\"endDate\":\"\",\"frequencyType\":null,\"numberOfOperations\":null},\"indicativeAmount\":"+amount+",\"cardDescription\":\"" + \
            cardName+"\",\"cardNumberMasked\":\""+self.maskedCardNumber+"\",\"typeCode\":0,\"numberMonths\":1}"

        response = self.session.post(url, json=json.loads(payload))
        operationId = str(response.json()["operationId"])
        url = "https://app.cgd.pt/pceApi/rest/v1/business/cards/mbnet/card/executions"

        payload = "{\"operationId\":"+operationId+",\"operationName\":\"\",\"operationEmail\":null,\"forceDuplicateOperation\":false,\"scheduling\":{\"startDate\":\"\",\"endDate\":\"\",\"frequencyType\":null,\"numberOfOperations\":null},\"indicativeAmount\":"+amount+",\"cardDescription\":\"" + \
            cardName+"\",\"cardNumberMasked\":\""+self.maskedCardNumber+"\",\"typeCode\":0,\"numberMonths\":1}"


        response = self.session.post(url, json=json.loads(payload))
        if(response.status_code == 401 and response.json()["message"] == "Autenticação inválida" and response.headers["WWW-Authenticate"].strip()=="SMS_TOKEN"):
            print("WRITE OTP:")
            url = "https://app.cgd.pt/pceApi/rest/v1/business/cards/mbnet/card/executions"

            payload = "{\"operationId\":"+operationId+",\"operationName\":\"\",\"operationEmail\":null,\"forceDuplicateOperation\":false,\"scheduling\":{\"startDate\":\"\",\"endDate\":\"\",\"frequencyType\":null,\"numberOfOperations\":null},\"indicativeAmount\":"+amount+",\"cardDescription\":\"" + \
                cardName+"\",\"cardNumberMasked\":\""+self.maskedCardNumber+"\",\"typeCode\":0,\"numberMonths\":1}"
            
            headersTemp = self.session.headers.copy()
            headersTemp.update({
                'Authorization': 'SMS_TOKEN '+str(input()),
            })
            response = self.session.post(url, headers=headersTemp, json=json.loads(payload))
            
            if(response.status_code!=200):
                raise UnknownError();

            return response.text

        if(response.status_code!=200):
            if(response.status_code == 500):
                if(response.json()["type"] == "dup"):
                    raise UnknownError("A ação está duplicada, muda o nome do CC")
            raise UnknownError()

    def cards_mbway(self):
        url = f"https://app.cgd.pt/pceApi/rest/v1/business/cards/mbnet/cards/"+self.maskedCardNumber+"?cardType=T&cardState=TD"

        response = self.session.get(url)

        print(response.text)

    def get_main_card(self):
        url = "https://app.cgd.pt/pceApi/rest/v1/business/cards?targetCardOperationType=CARD_MBNET_SUBSCRIPTION&cardImage=true"

        response = self.session.get(url)

        self.maskedCardNumber = response.json()[0]["maskedCardNumber"]
        self.replaceMaskedCardNumber = response.json()[0]["maskedCardNumber"].replace(" ","")
