=======================
Unerwartet: def vs. val
=======================

:date: 2018-01-30 23:12
:tags: de, programming, scala

Nach einem Jahr der Blog-Abstinenz heute zur Erfrischung mal ein wenig Scala.
Nehmen wir an, wir haben die folgende ``login``-Funktion, die `REST-assured`_
nutzt, um HTTP-Requests für einen Login zu tätigen. Zurückgegeben wird ein Tupel
mit einem Access-Token und wie lange selbiges gültig ist.

.. code:: scala

   def login(credentials: Credentials): (String, Int) = {
     def json = given()
       // Skipped: add the credentials somehow to the request
       .post("…")
       .Then
       .statusCode(HttpStatus.SC_OK)
       .extract()
       .jsonPath()

     (json.getString("access_token"), json.getInt("expires_in"))
   }

Manchmal gibt die Methode ein Access-Token zurück, das nicht gültig ist, obwohl
es laut der ebenfalls zurückgegebenen Gültigkeitsdauer noch lange gültig sein
sollte. Warum?

Sehr subtil, aber das ``def json = …`` sollte natürlich ein ``val json = …``
sein. Ansonsten findet bei der Erstellung des Rückgabe-Tupel zwei mal ein Aufruf
der Funktion ``json`` statt: einmal bei der Auswertung von
``json.getString("access_token")`` und das andere Mal bei der Auswertung von
``json.getInt("expires_in")``. Beides mal wird natürlich auch ein frischer
HTTP-Request abgesetzt. Es konnte daher passieren, dass für das Access-Token ein
Token zurückgegeben wurde, das gerade am ablaufen ist, und für den
``expires_in``-Wert wurde bereits ein neues Token ausgestellt. Daher sieht es so
aus, als wäre das Token noch lange gültig, dabei ist es bereits abgelaufen.

.. _REST-assured: http://rest-assured.io/
