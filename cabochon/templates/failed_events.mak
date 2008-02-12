<h1>Cabochon admin console</h1>
<h2>Failed events</h2>

<table>
<tr>
<th>type</th>
<th>url</th>
<th>id</th>

<th>subscriber id</th> 
<th>number of failures</th>
<th>last tried</th>

</tr>
% for event in c.failed_events:
<tr id="event_${event.id}">
<td>${event.event_type.name}</td>
<td>${event.subscriber.url}</td>
<td>${event.id}</td>

<td>${event.subscriber.id}</td>
<td>${event.failures}</td>
<td>${event.last_sent}</td>
<td>${h.link_to("data", h.url_for(action="event_details", cls="failed", id=event.id))}</td>

<td>${h.secure_button_to("delete entirely", h.url_for(action="delete_failed_event", id=event.id))}</td>
<td>${h.secure_button_to("return to pending queue", h.url_for(action="retry_event", id=event.id))}</td>
</tr>
% endfor

</table>

Pages: ${ c.page_list }
