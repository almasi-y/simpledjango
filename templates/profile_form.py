<form method="POST" action = "">
        {% csrf_token %}
        {{ form.as_p }}
      <input type = "Submit" value = "Submit" />
</form>
