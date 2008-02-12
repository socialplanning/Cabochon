<h1>Cabochon admin console</h1>
<h2>Event details</h2>

<table>
<tr>
<th>type</th>
<th>url</th>
<th>id</th>

<th>subscriber id</th> 
<th>number of failures</th>
<th>last tried</th>

</tr>
<tr id="c.event_${c.event.id}">
<td>${c.event.event_type.name}</td>
<td>${c.event.subscriber.url}</td>
<td>${c.event.id}</td>

<td>${c.event.subscriber.id}</td>
<td>${c.event.failures}</td>
<td>${c.event.last_sent}</td>

<td>${h.secure_button_to("delete entirely", h.url_for(action="delete_failed_c.event", id=c.event.id))}</td>
<td>${h.secure_button_to("return to pending queue", h.url_for(action="retry_c.event", id=c.event.id))}</td>
</tr>

</table>

Data:

${h.pformat(c.data)}