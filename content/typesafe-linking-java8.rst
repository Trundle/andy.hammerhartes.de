================================
Typsicheres verlinken mit Java 8
================================

:date: 2016-01-10 22:01:20
:tags: programming, java, web
:status: draft


Im heutigen Blog-Post geht es um Webrahmenwerke. Genauer: es geht darum, wie man
Links zu Controllern erzeugt, auf typsichere Art und Weise. Typsicher in dem
Sinne, dass man Variablen im Routing nur durch Werte von dem Typ ersetzen kann,
den der Controller auch erwartet. Übergibt man die falsche Anzahl an Werten oder
Werte vom falschen Typ, soll der Code erst gar nicht kompilieren (in anderen
Worten: keine Exceptions zur Laufzeit). Wir beschränken uns auf Pfad-Variablen.

Die Code-Beispiele für die Controller sind lose an `JAX-RS
<https://en.wikipedia.org/wiki/Java_API_for_RESTful_Web_Services>`_ orientiert.
Die folgenden Konventionen werden benutzt:

* Methoden, die Requests behandeln, haben lediglich die Pfad-Variablen als
  Parameter, in der Reihenfolge, in der sie im Routing-Template definiert sind

.. note::

   In dem Blog-Beitrag wird nur die Methode vorgestellt, mit der man Links
   erstellen kann. Ein Router, der Requests auf Controller dispatcht, wird nicht
   vorgestellt.

   Außerdem wird eine gewisse Vertrautheit mit Java 8 (insbesondere Lambdas)
   vorausgesetzt sowie auch ein wenig mit JAX-RS.


Prior Art
=========

Da *Links erzeugen* ein Recht häufig Problem ist, gibt es natürlich so einiges
an Prior Art. Wahrscheinlich in so ziemlich jedem Webrahmenwerk, in den
unterschiedlichsten Ausprägungen. Ich habe stellvertretend einmal drei
herausgegriffen:

* `Pyramids route_url
  <http://pyramid.readthedocs.org/en/latest/api/request.html#pyramid.request.Request.route_url>`_

  Zeigt schon mal die grobe Idee. Gewisse Fehler werden abgefangen (falsche
  Anzahl an Argumenten zum Beispiel). Allerdings passiert alles zur Laufzeit.
  Man braucht also eine recht gut ausgeprägte Test-Suite, um Fehler beim Linken
  zu erkennen.
* `Declarative Hyperlinking in Jersey <https://jersey.java.net/documentation/latest/declarative-linking.html>`_

  Mit Annotationen umgesetzt und dadurch stringly typed. Fehler werden erst zur
  Laufzeit erkannt.
* `Spring HATEOAS <http://projects.spring.io/spring-hateoas/>`_

  Kommt schon recht nahe dran. Insbesondere `Building links pointing to methods
  <http://docs.spring.io/spring-hateoas/docs/0.19.0.RELEASE/reference/html/#fundamentals.obtaining-links.builder.methods>`_
  geht stark in die Richtung:

  .. code:: java

     Method method = PersonController.class.getMethod("show", Long.class);
     Link link = linkTo(method, 2L);

  Allerdings funktioniert die Methoden-Auflösung zur Laufzeit und via Name als
  String. Die Parametertypen müssen explizit angegeben werden und die
  Typüberprüfung passiert auch erst zur Laufzeit.


Warum nicht Methodenreferenzen?
===============================

Da Java 8 endlich Methodenreferenzen eingeführt hat, liegt natürlich die Idee
nahe, es damit irgendwie zu versuchen.

Stellen wir uns vor, dass wir den folgenden Controller hätten:

.. code:: java

   @Path("/hello")
   class HelloWorldController {

       @GET
       public String hello() {
           return "Hello, world!";
       }
   }

Als erstes erstellen wir ein `FunctionalInterface
<http://docs.oracle.com/javase/8/docs/api/java/lang/FunctionalInterface.html>`_.
Das Interface soll eine Referenz auf eine Methode der Klasse ``H`` darstellen,
die keine Parameter entgegen nimmt und ein ``R`` als Ergebnis zurück gibt.
Dementsprechend sieht das Interface wie folgt aus:

.. code:: java

   @FunctionalInterface
   interface NoParam<H, R> {
       R apply(H h);
   }

Dieses Interface kann aus einer Methodenreferenz erstellt werden:

.. code:: java

   NoParam<HelloWorldController, String> hello = HelloWorldController::hello;
   // Aufrufen könnte man die Methode jetzt so (angenommen,
   // someHelloWorldController ist eine Instanz von HelloWorldController):
   String result = hello.apply(someHelloWorldController);
   assert "Hello, world!".equals(result);

Folglich können wir damit dann die folgende Methode bauen:

.. code:: java

   <H, R> URI linkTo(NoParam<H, R> handler) {
       // Hier der Code, der die Routing-Informationen von handler ausliest und
       // daraus dann eine URI baut
   }

Jetzt ist es möglich, aus einem anderen Controller heraus einen Link zu unserer
gewünschten Methode ``HelloWorldController#hello()`` zu bauen:

.. code:: java

   URI helloLink = linkTo(HelloWorldController::hello);

Wenn wir ein Argument zu viel übergeben würden (zum Beispiel, weil wir
denken, dass die hello-Ressource einen Namen entgegen nimmt, um einen
personalisierten Gruß zu erzeugen, kompiliert der Code nicht::

   java: no suitable method found for linkTo(HelloWorldController::hello)

Ziel erreicht. Um tatsächlich Pfad-Parameter zu unterstützen, müssen wir jetzt
einfach (relativ mechanisch) weitere Interfaces einführen.

Erweitern wir zunächst unseren Controller um einen personalisierten Gruß:

.. code:: java

   @GET
   @Path("/{name}")
   public String greeting(String name) {
       return "Hello, " + name + "!";
   }

Der Parameter ``name`` repräsentiert hierbei die Pfad-Variable ``name``.
Pfad-Variablen Links dazu wollen wir dann folgenderweise erstellen:

.. code:: java

   URI link = linkTo(HelloWorldController::greeting, "Joe");

Dazu führen wir ein weiteres Interface ein:

.. code:: java

   @FunctionalInterface
   interface OneParam<H, P, R> {
       R apply(H h, P p);
   }

Wenig überraschend steht ``H`` hierbei für den Typ des Controllers, ``P`` für
den Parameter und ``R`` für den Rückgabewert.

Desweiteren muss eine weitere Überladung von ``linkTo`` eingeführt werden:

.. code:: java

   URI linkTo(OneParam<H, P, R> handler, P param) {
       // Hier wieder Routing-Infos von handler auslesen und dann param einsetzen
   }

Das ist zum Implementieren zwar ein wenig wortreich (für jede Anzahl an
Pfad-Variablen ein eigenes Interface und eine entsprechende ``linkTo``-Methode),
aber das muss man ja nur einmal tun und außerdem hat man ja auch nicht unendlich
lange Pfade in der Praxis.

Viel gravierender ist jedoch: es funktioniert überhaupt nicht. Man kann zwar aus
einer Methodenreferenz ein Lambda bauen. Allerdings geht die Information, aus
welcher Methode das Lambda erzeugt wird, dabei verloren. Wir brauchen die
Information, um welche Methode es sich handelt, jedoch, da wir ansonsten nicht
an die Route kommen.


Proxies to the rescue
=====================

Da die Antwort auf die meisten Probleme in Java "(dynamische) Code-Generierung"
ist, probieren wir es doch auch einmal damit. Genauer gesagt dynamische
Proxy-Objekte. Die Idee ist dabei folgendermaßen:

* Wir erzeugen uns ein Proxy-Objekt vom gleichen Typ der Handler-Klasse.
* Wir rufen die Methode auf, die übergeben wurde (genauer gesagt, das Lambda)
* Das Proxy-Objekt ruft nicht wirklich die eigentliche Methode auf, sondern
  merkt sich einfach, welche Methode aufgerufen wurde.
* Wir holen uns die gemerkte Methode vom Proxy-Objekt.

Gehen wir davon aus, dass wir eine Klasse ``MethodResolver<T>``, die die
Proxy-Objekte erstellt, könnte unsere ``linkTo``-Methode also in der Art
aussehen:

.. code:: java

   URI linkto(Class<H> handlerClass, OneParam<H, P, R> handler, P param) {
       MethodResolver<H> methodResolver = MethodResolver.on(handlerClass);
       handler.apply(methodResolver, param);
       Method method = methodResolver.resolve();
       // Mit handlerClass und method kann man jetzt an die Routing-Informationen
       // kommen
   }

Die meisten AOP-Rahmenwerke bieten Method-Interceptors an, mit denen man das
recht einfach umsetzen kann. Für `Proxetta
<http://jodd.org/doc/proxetta/index.html>`_ könnte ein entsprechendes Advice zum
Beispiel so aussehen:

.. code:: java

   /**
    * MethodResolver advice applied on all methods. It puts the method in a class
    * variable that can be accessed later using reflection.
    */
   class MethodResolverAdvice implements ProxyAdvice {

       public Method method;
   
       public Object execute() {
           final Class<?> targetClass = targetClass();
           final String methodName = targetMethodName();
           final Class<?>[] argumentTypes = createArgumentsClassArray();
           try {
               method = targetClass.getMethod(methodName, argumentTypes);
           } catch (NoSuchMethodException e) {
               throw new RuntimeException(e);
           }
           return returnValue(null);
       }
   }


Beispielimplementierung
=======================

Im Github-Repo `java8_linking_experiments
<https://github.com/Trundle/java8_linking_experiments>`_ habe ich eine
Beispielimplementierung für das `Ratpack-Mikro-Webrahmenwerk
<https://ratpack.io/>`_ umgesetzt.
