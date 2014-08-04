import org.jsoup.Jsoup;
import org.jsoup.helper.Validate;
import org.jsoup.nodes.Document;
import org.jsoup.nodes.Element;
import org.jsoup.select.Elements;
import scala.language.implicitConversions
import java.io.PrintWriter
import scala.util.parsing.json.JSONArray
import com.google.gson.GsonBuilder

object Parser {
  case class Candidate(name: String, url: String, born: String, party: String, address: String, edu: String, firm: String, job: String, dep: String, criminal: String, status: String )
  case class Election()

  def getElectionList(url: String): List[(String, String)] = {
    val doc = Jsoup.connect(url).timeout(20000).get();
    val vibLinks = doc.select(".vibLink").map(x=>(x.attr("href"), x.text))
    return vibLinks
  }

  def getObj(url: String) : List[Any] = {
    val elList = getElectionList(url).view.filter(_._2 contains "Красногорск").toList
    val res = for (e <- elList;
                   page = getCandidatesPage(e._1) if page._1 != "")
                     // name, date, url, infos
                      yield Array(e._2, page._2, e._1, getCandidatesLinks(page._1).map(getCandidateData).map(_.toArray).toArray)
    res
  }
  def saveJson(obj: List[Any]) {
    val gson = new GsonBuilder().disableHtmlEscaping().create();
    Some(new PrintWriter("elections.json")).foreach{p =>
      p.write(gson.toJson(obj.toArray)); p.close
    }
  }


  def getCandidateData(tuple: (String, String, String, String)) : List[String] = {
    val doc = Jsoup.connect(tuple._1).timeout(20000).get();
    val tbody = doc.select("td:containsOwn(Общие сведения)").first().parent().parent()
    val tds = tbody.select("td").drop(3).zipWithIndex.filter(x => (x._2 + 1) % 3 == 0).map(_._1.text.trim)

    tds match {
      case List(a, b, c, d, e, f, g, h, i) => List(a, tuple._1, tuple._2, tuple._3, c, d, e, f, g, h, i, tuple._4)
    }
  }

  def getCandidatesPage(url: String) : (String, String) = {
    val doc = Jsoup.connect(url).timeout(20000).get();

    println(url)
    val pageElements = doc.select("a:containsOwn(Сведения о кандидатах)")
    if (pageElements.size > 0) {
      val page = pageElements.first().attr("href")
      val dateString = doc.select("td:contains(Дата голосования)").get(1).parent.child(1).text
      return (page, dateString)
    } else {
      return ("", "")
    }
  }

  implicit def Elements2List(elements: Elements) : List[Element] = {
    val a = new Array[Element](0)
    elements.toArray(a).toList
  }

  def getFirstInfo(e: Element) : (String, String, String, String) = {  // from tr get link, born date and party
    val link = e.select("a").first().attr("href")
    val date = e.child(2).text
    val party = e.child(3).text
    val district = e.child(4).text
    return (link, date, party, district)
  }

  def getCandidatesLinks(url: String): List[(String, String, String, String)] = {
    def step(url: String, pageN: Int, acc: List[(String, String, String, String)]) : List[(String, String, String, String)] = {
      val urlWithN = url + "&number=" + pageN.toString  // increment pageN while "test" id exist
      val doc = Jsoup.connect(urlWithN).timeout(20000).get();
      val elements = doc.select("tbody[id=test] tr")
      if (elements.size == 0) acc
      else {
        val listOfCanditatesLinks = elements.map(getFirstInfo)
        println(listOfCanditatesLinks)
        step(url, pageN+1, acc ++ listOfCanditatesLinks)
      }
    }
    step(url, 1, List[(String, String, String, String)]())
  }

  def main(args: Array[String]) {
    val url = "http://www.moscow_reg.vybory.izbirkom.ru/region/region/moscow_reg"
    val obj = getObj(url)
    saveJson(obj)
  }
}
