from bs4 import BeautifulSoup, SoupStrainer
import urllib.request
from elections_app.models import Person, Info, Election
from datetime import datetime, timedelta
import json
import django
import logging


logger = logging.getLogger('elections')

def get_soup(url):
  response = urllib.request.urlopen(url)
  html = response.read().decode("cp1251", 'ignore')
  html = "".join(line.strip() for line in html.split("\n"))
  return BeautifulSoup(html, "html.parser")

def fix_link(url):  # some strage behavior of non-unicode character
  return url.replace("®", "&reg")

def load_from_url(root_url, html_text, filter_string):
  logger.info('Стартует загрузка данных по выборам')
  if html_text:
    html = "".join(line.strip() for line in html_text.split("\n"))
    soup = BeautifulSoup(html, "html.parser")
  else:
    soup = get_soup(root_url)
  vib_links = soup.find_all('a', class_ ="vibLink")
  election_urls = [[a.text.strip(), fix_link(a['href'])] for a in vib_links if filter_string == "" or filter_string.lower() in a.text.lower()]
  logger.info('Начинается загрузка, число выборов в списке - %s' % len(election_urls))
  for elem in election_urls:
    soup = get_soup(elem[1])

    name = elem[0]
    url = elem[1]
    candidates_link = soup.find("a", text="Сведения о кандидатах")

    date_elem = soup.find(text="Дата голосования")
    if date_elem:
      date_text = date_elem.parent.parent.parent.find_all("td")[1].text
      date = datetime.strptime(date_text, '%d.%m.%Y')
    else:
      logger.info('Нет даты голосования для %s' % name)
      continue

    try:
      election = Election.objects.get(name=name, date=date)
      if filter_string == "" and django.utils.timezone.now() - election.updated_at < timedelta(hours=12):  # if without filter and last update too close
        logger.info('Выборы обновлялись меньше чем 12 часов назад %s' % name)
        continue
      if election.url != url:
        election.url = url
    except Election.DoesNotExist:
      election = Election(name=name, date=date, url=url)
      election.save()

    if not candidates_link:
      logger.info('Нет линка на кандидадтов %s' % name)
      continue

    load_cantidates_from_url(fix_link(candidates_link['href']), election)
    election.save()  # date update anyway

    delete_old_infos(election)  #sometimes TIKs change candidate date, need to remove old

  logger.info("ЗАГРУЗКА ПРОШЛА НОРМАЛЬНО, все выборы отбработаны")

def delete_old_infos(election):
  currentInfos = Info.objects.filter(election=election)
  for info in currentInfos:
    if election.updated_at - info.updated_at > timedelta(hours=12):
      logger.info('Удаляем инфу кандидата %s' % info.person)
      info.delete()

def load_cantidates_from_url(url, election):
  i = 1
  while True:
    soup = get_soup(url+"&number="+str(i))
    i += 1
    table = soup.find(id="test")
    if not table:
      logger.info('Нет таблицы кандидатов для %s' % election.name)
      break
    trs = table.find_all("tr")
    if len(trs) == 0:
      logger.info('Таблица кандидатов пустая %s' % election.name)
      break
    for tr in trs:
      data = tr.find_all("td")
      name = data[1].contents[0].contents[0].text.strip()  # in nobr tag
      logger.info('Загружен кандидат %s, выборы %s' % (name, election.name))
      link = fix_link(data[1].contents[0].contents[0]['href'])
      date = datetime.strptime(data[2].text, '%d.%m.%Y')
      party = data[3].text.strip()
      district = data[4].text.strip()

      try:
        person = Person.objects.get(name=name, birthdate=date)
      except Person.DoesNotExist:
        person = Person(name=name, birthdate=date)
        person.save()

      try:
        info = Info.objects.get(person=person, election=election)
      except Info.DoesNotExist:
        info = Info(person=person, election=election)
        info.save()

      load_info(link, party, district, info)


def load_info(link, party, district, info):
  soup = get_soup(link)
  table = soup.find(text="Общие сведения").parent.parent.parent
  tds = table.find_all("td")[3:]  # drop first 3
  res = []
  for i, td in enumerate(tds):
    if (i+1) % 3 == 0:
      res.append(td.text.strip())
  info.url = link
  info.party = party
  info.district = district
  info.address = res[2].strip()
  info.edu = res[3].strip()
  info.firm = res[4].strip()
  info.job = res[5].strip()
  info.dep = res[6].strip()
  info.criminal = res[7].strip()
  info.status = res[8].strip()
  make_exclusion(info)
  info.save()


def make_exclusion(info):
  if info.person.id == 30187:  # Красюков Александр Сергеевич - 1978-01-07, личная просьба убрать
    info.criminal = ""


def load_from_json(json_file):
  data = json.loads(json_file.read().decode('utf-8'))
  for d in data:
    name = d[0]
    date = datetime.strptime(d[1], '%d.%m.%Y')
    url = d[2]
    try:
      election = Election.objects.get(name=name, date=date)
      if election.url != url:
        election.url = url
        election.save()
    except Election.DoesNotExist:
      election = Election(name=name, date=date, url=url)
      election.save()


    candidates = d[3]
    for c in candidates:
      try:
        person = Person.objects.get(name=c[0], birthdate=datetime.strptime(c[2], '%d.%m.%Y'))
      except Person.DoesNotExist:
        person = Person(name=c[0], birthdate=datetime.strptime(c[2], '%d.%m.%Y'))
        person.save()

      try:
        info = Info.objects.get(person=person, election=election)
      except Info.DoesNotExist:
        info = Info(person=person, election=election)
        info.save()
      info.url = c[1]
      info.party = c[3]
      info.address = c[4]
      info.edu = c[5]
      info.firm = c[6]
      info.job = c[7]
      info.dep = c[8]
      info.criminal = c[9]
      info.status = c[10]
      info.district = c[11]
      info.save()
