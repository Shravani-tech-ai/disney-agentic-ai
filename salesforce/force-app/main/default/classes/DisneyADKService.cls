public with sharing class DisneyADKService {
    public class ADKException extends Exception {}
    public static Map<String,Object> sendMessage(String sessionId, String message, String userId) {
        Disney_Integration_Config__mdt cfg = DisneyAgentConfigService.getIntegrationConfig();
        if (cfg == null || cfg.Is_Active__c != true) throw new ADKException('Disney ADK integration is disabled in Custom Metadata.');
        List<String> enabled = new List<String>();
        for (DisneyAgentConfigService.AgentInfo a : DisneyAgentConfigService.getEnabledAgents()) enabled.add(a.name);
        Map<String,Object> payload = new Map<String,Object>{
            'session_id' => sessionId, 'user_id' => userId, 'message' => message,
            'configuration' => new Map<String,Object>{'mock_mode' => cfg.Mock_Mode__c, 'enabled_agents' => enabled}
        };
        HttpRequest req = new HttpRequest(); req.setEndpoint('callout:Disney_ADK_NC/api/chat'); req.setMethod('POST');
        Integer timeoutMs = cfg.Timeout_Seconds__c == null ? 30000 : cfg.Timeout_Seconds__c.intValue() * 1000;
        req.setTimeout(Math.min(Math.max(timeoutMs, 5000), 120000)); req.setHeader('Content-Type','application/json');
        req.setBody(JSON.serialize(payload));
        HttpResponse res = new Http().send(req);
        if (res.getStatusCode() < 200 || res.getStatusCode() >= 300) throw new ADKException('ADK service returned HTTP ' + res.getStatusCode() + '.');
        Map<String,Object> body = (Map<String,Object>)JSON.deserializeUntyped(res.getBody());
        if (body == null) throw new ADKException('ADK service returned an empty response.');
        return body;
    }
}
