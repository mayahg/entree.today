import os
import datetime
from datetime import timedelta
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from dotenv import load_dotenv
load_dotenv() 
import json

cred = credentials.Certificate(json.loads(os.environ.get('key')))
firebase_admin.initialize_app(cred)
db = firestore.client()


"""
Returns meal (lunch or dinner) based on time of day. If its before 4 pm, returns lunch (or brunch if a weekend). Otherwise returns dinner.
"""
def getMeal(dateTime):
    hour = int(dateTime[11:13])
    if hour == 22 or hour == 23 or (hour >= 0 and hour < 7):
        return 'dinner'
    elif datetime.datetime.today().weekday() > 4:
            return 'brunch'
    return 'lunch'
    

"""
Returns current date in pacific time.
"""
def getDatePT(dateTime):
    hour = int(dateTime[11:13])
    if hour < 7:
        return str(datetime.date.today() - timedelta(days=1))
    return str(datetime.date.today())


"""
Returns list of dishes on the specified date and for the specified meal. Takes in the current hour to compute the correct date.
"""
def getDishes(date, meal):
    foodsActual = db.collection(u'FoodsActual')
    if meal == 'lunch' or meal == 'brunch':  #will display the lunch. parts of brunch
        meals = foodsActual.where(u'Date', u'==', u"" + date +"").where(u'Meal', u'==', u'lunch').order_by('Index')
    else:
        meals = foodsActual.where(u'Date', u'==', u"" + date +"").where(u'Meal', u'==', u'dinner').order_by('Index')
    docs = meals.stream()
    final = []
    for doc in docs:
        dish = (doc.to_dict()['Dish']).lower()
        if dish not in final: #Protect against displaying duplicates in databse, because WayScript likes to scrape twice sometimes.
            final.append(dish)
    return final #implement meal logic


"""
Creates string of HTML to be inserted, which is comprised of the first two dishes listed.
"""
def writeEntrees(dishes):
    entrees = """
        <p class="p-4 text-xl">
            %s
        </p>
        <p class="p-4 text-xl">
            %s
        </p>
        """ 
    if len(dishes) < 2:
        return "error"
    return(entrees % (dishes[0], dishes[1]))

"""
Creates string of HTML to be inserted, which is comprised of all but the first two dishes listed.
"""
def writeSides(dishes):
    sides = ""
    new = ""
    newish = ""
    for side in dishes[2:]:
        new = """
        <p class="p-4 text-xl">
            %s
        </p>
        """
        newish = new % side
        sides = sides + newish
    return(sides)

"""
Creates new index.html file comprised of the proper meal and dishes.
"""
def writeFile(dishes, meal):
    path = os.environ.get('GITHUB_WORKSPACE') + '/website/dist/index.html'
    f = open(path,'w')
    if len(dishes) < 2:
        message = """ 
        <!DOCTYPE html>
            <html>
            <head>
                <title>entree.today</title>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <link href="output.css" rel="stylesheet"> 
                <link rel="shortcut icon" type="image/x-icon" href="favicon.ico">
                <script defer src="/_vercel/insights/script.js"></script>
            </head>
            <body>
            <div class="bg-no-repeat bg-cover bg-opacity-20 sm:bg-right-bottom min-h-screen"
                style="background-image: url(FinalFinal50.png)">
                <div class="p-4 md:grid md:grid-cols-5">
                    <div class="md:col-start-2 md:col-end-5"> 
                        <div>
                            <h1 class="heading text-6xl font-bold md:text-center" id="top">%s</h1>
                            <div id="info" class="md:text-center md:text-xl italic">
                            %s
                            </div>
                        </div>
                        <div class="py-6" >
                            <h1 class="heading py-2 font-bold md:text-center" id="entree_header" align="center">SORRY</h1>
                            <div id="entrees" class="md:text-center md:text-xl">
                                Either our systems experienced an error, or Stanford's dining hall menu site isn't displaying info today.
                                This may be because Stanford's dining halls aren't open today. 
                            </div>
                        </div>
                        <div class="footer pt-24 text-xs bottom-0" align="center">
                            <p class="text-[6px] w-96 text-zinc-400"><i>Background image recolored from original by Ward & Blohme, Architects. Memorial Church. August 1, 1911. Sourced from <u><a href="https://searchworks.stanford.edu/view/zy932bd0293">Stanford Library</a></u>. <a target="_blank" href="https://icons8.com/icon/59873/restaurant">Restaurant</a> icon by <a target="_blank" href="https://icons8.com">Icons8</a>.</i></p>
                        </div>
                    </div>
                </div>
            </div> 
            </body>
        </html>
        """

    else: 
            message = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>entree.today</title>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <link href="output.css" rel="stylesheet"> 
                <link rel="shortcut icon" type="image/x-icon" href="favicon.ico">
                <script defer src="/_vercel/insights/script.js"></script>
            </head>
            <body>
            <div class="bg-no-repeat bg-cover bg-opacity-20 sm:bg-right-bottom min-h-screen"
                style="background-image: url(FinalFinal50.png)">
                <div class="p-4 md:grid md:grid-cols-5">
                    <div class="md:col-start-2 md:col-end-5"> 
                        <div>
                            <h1 class="heading text-6xl font-bold md:text-center" id="top">%s</h1>
                            <div id="info" class="md:text-center md:text-xl italic">
                            %s
                            </div>
                        </div>
                        <div class="py-6" >
                            <h1 class="heading py-2 font-bold md:text-center" id="entree_header" align="center">ENTREES</h1>
                            <div id="entrees" class="md:text-center md:text-xl">
                                %s
                            </div>
                        </div>
                        <div  class="py-6" >
                            <h1 class="heading font-bold py-2 md:text-center" id="sides_header" align="center">SIDES</h1>
                            <div  id="sides" class="md:text-center md:text-xl">
                                %s
                            </div>
                        </div>
                        <div class="footer pt-8 text-xs" align="center">
                            <p class="text-[6px] w-96 text-zinc-400"><i>Background image recolored from original by Ward & Blohme, Architects. Memorial Church. August 1, 1911. Sourced from <u><a href="https://searchworks.stanford.edu/view/zy932bd0293">Stanford Library</a></u>. <a target="_blank" href="https://icons8.com/icon/59873/restaurant">Restaurant</a> icon by <a target="_blank" href="https://icons8.com">Icons8</a>.</i></p>
                        </div>
                    </div>
                </div>
            </div> 
            </body>
        </html>
        """
    info = ""
    if meal == 'brunch':
        info = 'This is supposed to be the lunch part of brunch. Expect breakfast food too.'
    whole = message % (meal.upper(), info, writeEntrees(dishes), writeSides(dishes))
    f.write(whole)
    f.close()


def writeAPI(date, meal, dishes):
    path = os.environ.get('GITHUB_WORKSPACE') + '/website/dist/api.json'
    f = open(path,'w')
    message = """{"date": %s, "meal": %s, "entrees": %s, "sides": %s}"""
    full = message % (date, meal, dishes[0:2], dishes[2:])
    f.write(full)
    f.close()

    
if __name__ == "__main__":
    dateTime = str(datetime.datetime.utcnow())
    date = getDatePT(dateTime)
    meal = getMeal(dateTime)
    print(meal)
    dishes = getDishes(date, meal)
    writeFile(dishes, meal)
    writeAPI(date, meal, dishes)
