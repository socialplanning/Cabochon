<h1>Cabochon admin console</h1>

<table>
<tr>
<th>url</th>
<th>id</th> 
<th>number of pending events</th>
<th>number of failed events</th>
<th></th>
</tr>
% for subscriber in c.subscribers:
<tr id="subscriber_${subscriber.id}">
<td>${subscriber.url}</td>
<td>${subscriber.id}</td>
<td>${len(subscriber.pending_events)}</td>
<td>${len(subscriber.failed_events)}</td>
<td>${h.secure_button_to("unsubscribe", h.url_for(action="unsubscribe", id=subscriber.id))}</td>
<td>${h.secure_button_to("retry all failed events", h.url_for(action="retry_all_failed_events", id=subscriber.id))}</td>
</tr>
% endfor

</table>

<hr>
Things you can do:
<ul>
<li>${h.link_to("Manage pending events", h.url_for(action="pending_events"))}</li>
<li>${h.link_to("Manage failed events", h.url_for(action="failed_events"))}</li>
