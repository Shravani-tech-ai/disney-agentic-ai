public with sharing class DisneyAgentController {
    @AuraEnabled(cacheable=true)
    public static List<DisneyAgentConfigService.AgentInfo> getAgents() { return DisneyAgentConfigService.getEnabledAgents(); }
    @AuraEnabled
    public static Map<String,Object> chat(String message, String sessionId) {
        if (String.isBlank(message)) throw new AuraHandledException('Please enter a message.');
        if (message.length() > 4000) throw new AuraHandledException('Please keep your message under 4,000 characters.');
        String sid = String.isBlank(sessionId) ? 'SF-' + UserInfo.getUserId() + '-' + String.valueOf(DateTime.now().getTime()) : sessionId;
        try { return DisneyADKService.sendMessage(sid, message.trim(), UserInfo.getUserId()); }
        catch (Exception e) { throw new AuraHandledException('Unable to contact the Disney assistant: ' + e.getMessage()); }
    }
    
    @AuraEnabled
    public static String getTrace(String traceId) {

        if (String.isBlank(traceId)) {
            throw new AuraHandledException('Trace ID is required.');
        }

        HttpRequest req = new HttpRequest();

        req.setEndpoint(
            'callout:Disney_ADK_NC/api/observability/traces/'
            + EncodingUtil.urlEncode(traceId, 'UTF-8')
        );

        req.setMethod('GET');
        req.setTimeout(120000);

        Http http = new Http();
        HttpResponse res = http.send(req);

        if (res.getStatusCode() >= 200 &&
            res.getStatusCode() < 300) {

            return res.getBody();
        }

        throw new AuraHandledException(
            'Unable to retrieve trace: ' + res.getBody()
        );
    }
    
    @AuraEnabled
    public static String getMetrics() {

        HttpRequest req = new HttpRequest();

        req.setEndpoint(
            'callout:Disney_ADK_NC/api/observability/metrics'
        );

        req.setMethod('GET');
        req.setTimeout(120000);

        Http http = new Http();

        HttpResponse res = http.send(req);

        if (res.getStatusCode() >= 200 &&
            res.getStatusCode() < 300) {

            return res.getBody();
        }

        throw new AuraHandledException(
            'Unable to retrieve metrics: ' + res.getBody()
        );
    }
}
