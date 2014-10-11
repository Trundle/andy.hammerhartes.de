Generic Heterogenous Containers Using Super Type Tokens
=======================================================

:date: 2014-08-24 01:55
:tags: de, java, generics


Wie man am Titel bereits leicht erraten kann: heute geht es (zum
ersten Mal in diesem Blog?) um Java. Genauer: Wie man heterogene
Container in Java umsetzen kann.

Zunächst zur Idee: Wir wollen eine Klasse ``Favorites``
implementieren, in die man seine Lieblingsobjekte speichern und auch
wieder abrufen kann. Damit man nicht einfach irgendein beliebiges
Objekt zurückbekommt, sondern ein Objekt von einem bestimmten Typ,
übergibt man beim Speichern und abrufen die Klasse des Objekts.

Die API dafür sieht so aus:

.. code-block:: java

   public class Favorites {
       public <T> void putFavorite(Class<T> type, T instance);
       public <T> getFavorite(Class<T> type);
   }

.. note:: Der geneigte Java-erfahrene Leser wird direkt erkennen, dass
          das Beispiel aus *Effective Java* von Joshua Bloch ist. Das
          ist absolut richtig und auch Teile des hier gezeigten Codes
          stammen aus diesem Buch, das durchaus lesenswert ist (auch
          für Nicht-Java-Programmierer).

Die erste Idee, das zu implementieren, könnte etwa so aussehen:

.. code-block:: java

   public class Favorites {
       private final Map<Class<?>, Object> favorites = new HashMap<>();

       public <T> void putFavorite(Class<T> type, T instance) {
           favorites.put(checkNotNull(type), instance);
       }

       public <T> T getFavorite(Class<T> type) {
           return type.cast(favorites.get(type));
       }
   }

Man nimmt also einfach das Klassenobjekt des Werts als Schlüssel in
einer Map, um den Wert zu speichern. Beim Auslesen wird dann auch
wieder das Klassenobjekt übergeben, womit man an den Wert kommt. Wurde
für den Typ kein Wert hinterlegt, wird einfach nichts gefunden.

An sich scheint das auch ganz gut zu funktionieren:

.. code-block:: java

   Favorites f = new Favorites();
   f.putFavorite(String.class, "Some string");
   f.putFavorite(Integer.class, 1234);
   System.out.printf("%s %d%n", f.getFavorite(String.class), f.getFavorite(Integer.class));

Auch der Fall, dass kein Wert hinterlegt wurde für den Typ,
funktioniert einfach: ``favorites.get(type)`` gibt dann ``null``
zurück und ``null`` kann zu allem gecastet werden.


Und hätte Java jetzt nicht `Type Erasure
<http://en.wikipedia.org/wiki/Type_erasure>`_, wäre der Blogpost auch
schon zu Ende. Da Java allerdings Type Erasure hat, stößt man recht
bald auf ein Problem, wenn man auf versucht, ein Generic in den
Container zu packen: ``List<Integer>.class`` ist ein Syntaxfehler. Das
liegt daran, dass ``List<Integer>`` und ``List<String>`` dasselbe
Klassenobjekt haben, nämlich ``List.class``. Das bedeutet aber auch,
dass man eine Liste von Strings in ``Favorites`` packen kann und
danach als Liste von Integern auslesen kann (bzw. man kann es
zumindest versuchen):

.. code-block:: java

   f.putFavorite(List.class, Arrays.asList("foo", "bar"));
   List<Integer> values = f.getFavorite(List.class);

Wenn man das jetzt ausführt, scheint es sogar zu
funktionieren. Jedenfalls läuft es anstandslos durch. Allerdings nur
bis man dann den Wert tatsächlich einmal versucht als den angegebenen
Wert zu verwenden:

.. code-block:: java

   Integer first = values.get(0);

Bei einer erneuten Ausführung wird jetzt eine Ausnahme geworfen::

   Exception in thread "main" java.lang.ClassCastException: java.lang.String cannot be cast to java.lang.Integer

Bei genauem Hinschauen erkennt man auch bereits beim Kompilieren, dass
hier potenziell zur Laufzeit etwas kaputt gehen könnte::

   Favorites.java: warning: [unchecked] unchecked conversion
         List<Integer> values = f.getFavorite(List.class);
                                             ^
   required: List<Integer>
   found:    List

Ein gutes Beispiel dafür, dass man Compiler-Warnungen nicht einfach
ignorieren sollte.


Das ist natürlich wenig zufriedenstellend. Ein Ausweg daraus sind die
sogenannten `Super Type Tokens`_, die man wie folgt verwenden kann:

.. code-block:: java

   TypeReference<List<String>> x = new TypeReference<List<String>>() {};

``TypeReference`` kann jetzt zur Laufzeit nachsehen, welcher Wert als
Typvariable übergeben wurde. Das wiederum kann dann Favorite für sich
benutzen.

Die Implementierung von ``TypeReference``:

.. code-block:: java

   import java.lang.reflect.ParameterizedType;
   import java.lang.reflect.Type;
   
   public abstract class TypeReference<T> {
       private final Type type;
   
       protected TypeReference() {
           Type superClass = getClass().getGenericSuperclass();
           if (superClass instanceof Class<?>) {
               throw new RuntimeException("Missing type parameter");
           }
   
           type = ((ParameterizedType) superClass).getActualTypeArguments()[0];
       }
   
       public Type getType() {
           return type;
       }
   }

Und das angepasste ``Favorites``:

.. code-block:: java

   import java.lang.reflect.Type;
   import java.util.Arrays;
   import java.util.HashMap;
   import java.util.List;
   import java.util.Map;
   
   public class Favorites {
       private final Map<Type, Object> favorites = new HashMap<>();
   
       public <T> void putFavorite(TypeReference<T> typeReference, T instance) {
           favorites.put(typeReference.getType(), instance);
       }
   
       @SuppressWarnings("unchecked")
       public <T> T getFavorite(TypeReference<T> typeReference) {
           return (T) favorites.get(typeReference.getType());
       }
   
       public static void main(String[] args) {
           Favorites f = new Favorites();
           f.putFavorite(new TypeReference<String>() {}, "Some string");
           f.putFavorite(new TypeReference<Integer>() {}, 1234);
           f.putFavorite(new TypeReference<List<String>>() {}, Arrays.asList("foo", "bar"));
           System.out.printf("%s %d %s%n",
                             f.getFavorite(new TypeReference<String>() {}),
                             f.getFavorite(new TypeReference<Integer>() {}),
                             f.getFavorite(new TypeReference<List<Integer>>() {}));
       }
   }

Die Ausgabe ist wie erwartet ``Some string 1234 null``. Fertig ist er
also, unser typsicherer heterogener Container, der auch mit Generics
funktioniert (wenn auch etwas umständlich).

Oder fast. Wenn da dieses ``@SuppressWarnings("unchecked")`` nicht
wäre. Immerhin haben wir vor einem Augenblick erst gesehen, dass man
Compiler-Warnungen nicht ignorieren sollte. Und tatsächlich kann man
auch für die neue ``Favorites`` einen Fall konstruieren, bei dem zur
Laufzeit eine Ausnahme fliegt:

.. code-block:: java

   static <T> List<T> favoriteList(Favorites f) {
       TypeReference<List<T>> typeReference = new TypeReference<List<T>>(){};
       List<T> result = f.getFavorite(typeReference);
       if (result == null) {
           result = new ArrayList<T>();
           f.putFavorite(typeReference, result);
       }
       return result;
   }

   public static void main(String[] args) {
       Favorites f = new Favorites();
       List<String> listOfStrings = favoriteList(f);
       List<Integer> listOfIntegers = favoriteList(f);
       listOfIntegers.add(42);
       String booooom = listOfStrings.get(0);
   }

   // java.lang.ClassCastException: java.lang.Integer cannot be cast to java.lang.String

Um diese Ausnahme zu vermeiden, müsste man die Typ-Argumente
durchgehen und schauen, ob noch irgendwo eine `TypeVariable`
vorkommt. Ein Beispiel, in dem das gemacht wird, ist `GenericType<T>`_
aus JAX-RS_ (`Quelltext
<https://java.net/projects/jax-rs-spec/sources/git/content/src/jax-rs-api/src/main/java/javax/ws/rs/core/GenericType.java?rev=HEAD>`_). Das
würde aber noch immer zur Laufzeit eine Exception werfen und nicht zur
Compile-Zeit einen Fehler produzieren.

.. _GenericType<T>: https://jax-rs-spec.java.net/nonav/2.0.1/apidocs/javax/ws/rs/core/GenericType.html
.. _JAX-RS: https://jax-rs-spec.java.net/
.. _Jackson: https://github.com/FasterXML/jackson
.. _TypeReference<T>: https://fasterxml.github.io/jackson-core/javadoc/2.4/com/fasterxml/jackson/core/type/TypeReference.html

.. _Super Type Tokens: http://gafter.blogspot.de/2006/12/super-type-tokens.html
