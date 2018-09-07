import glob, os, json

def latestData(folder):
  files = glob.glob('Data/' + folder + '/*')
  if len(files) > 0:
    latest = max(files, key=os.path.getctime)
    return json.loads(open(latest).read())
  else:
    return {}

def allData(folder):
  files = glob.glob('Data/' + folder + '/*')
  return [json.loads(open(f).read()) for f in files]

def q():
  qScrapes = allData('Q Past Scrapes')
  qScrapes.append(latestData('Q Reports'))
  return qScrapes

def myHarvard():
  return latestData('my.harvard')

def qCourseIds():
  return latestData('Q Course Ids')