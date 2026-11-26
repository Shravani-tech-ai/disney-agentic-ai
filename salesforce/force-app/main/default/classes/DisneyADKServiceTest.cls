@IsTest
private class DisneyADKServiceTest {
    private class SuccessMock implements HttpCalloutMock {
        public HTTPResponse respond(HTTPRequest req) {
            System.assertEquals('POST', req.getMethod()); System.assert(req.getEndpoint().contains('Disney_ADK_NC'));
            Map<String,Object> sent=(Map<String,Object>)JSON.deserializeUntyped(req.getBody()); System.assertEquals('Hello Disney', (String)sent.get('message'));
            HttpResponse r=new HttpResponse(); r.setStatusCode(200); r.setHeader('Content-Type','application/json');
            r.setBody('{"success":true,"session_id":"SF-TEST","intent":"PRODUCT_KNOWLEDGE","selected_agents":["ProductKnowledgeAgent"],"answer":"Demo answer","data":{},"mock":true}'); return r;
        }
    }
    @IsTest static void chatReturnsBackendPayload() {
        Test.setMock(HttpCalloutMock.class,new SuccessMock());
        Test.startTest(); Map<String,Object> result=DisneyAgentController.chat('Hello Disney','SF-TEST'); Test.stopTest();
        System.assertEquals(true,result.get('success')); System.assertEquals('PRODUCT_KNOWLEDGE',result.get('intent'));
    }
    @IsTest static void blankMessageRejected() {
        try { DisneyAgentController.chat(' ','SF-TEST'); System.assert(false,'Expected validation error'); }
        catch (AuraHandledException e) { System.assert(e.getMessage().contains('message')); }
    }
}
