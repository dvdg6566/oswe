Boolean success = null;
String id = request.getParameter("id");
if(
	id != null && !id.isEmpty()
) {
	final Path LOGIN_REALM_IDENTITY = new Path("xri://@openmdx*org.openmdx.security.realm1/provider/CRX/segment/Root/realm/Default");

	String principalName = null;
	String providerName = null;
	String segmentName = null;
	
	int pos1 = id.indexOf("@");
	int pos2 = id.indexOf("/");
	if(pos1 > 0 && pos2 > pos1) {	
		// Format 1: principal@provider/segment
		principalName = id.substring(0, pos1);
		providerName = id.substring(pos1 + 1, pos2);
		segmentName = id.substring(pos2 + 1);
	} else if(pos1 > 0) {
		// Format 2: mail@domain
		javax.jdo.PersistenceManagerFactory pmf = org.opencrx.kernel.utils.Utils.getPersistenceManagerFactory();
		javax.jdo.PersistenceManager pmRoot = pmf.getPersistenceManager(
			SecurityKeys.ROOT_PRINCIPAL, 
			null
		);
        org.openmdx.security.realm1.jmi1.Segment realmSegment =
            (org.openmdx.security.realm1.jmi1.Segment)pmRoot.getObjectById(LOGIN_REALM_IDENTITY.getParent().getParent());
        int count = 0;
        for(org.openmdx.security.realm1.jmi1.Realm realm: realmSegment.<org.openmdx.security.realm1.jmi1.Realm>getRealm()) {
            if(!realm.refGetPath().equals(LOGIN_REALM_IDENTITY) && !"Root".equals(realm.refGetPath().getLastSegment().toClassicRepresentation())) {
       			String currentProviderName = realm.refGetPath().getSegment(2).toClassicRepresentation();
       			String currentSegmentName = realm.refGetPath().getLastSegment().toClassicRepresentation();
    			javax.jdo.PersistenceManager pm = pmf.getPersistenceManager(
					SecurityKeys.ADMIN_PRINCIPAL + SecurityKeys.ID_SEPARATOR + currentSegmentName, 
					null
				);
            	org.opencrx.kernel.home1.jmi1.Segment userHomeSegment = org.opencrx.kernel.backend.UserHomes.getInstance().getUserHomeSegment(pm, currentProviderName, currentSegmentName);
            	org.opencrx.kernel.home1.cci2.EMailAccountQuery emailAccountQuery = (org.opencrx.kernel.home1.cci2.EMailAccountQuery)org.openmdx.base.persistence.cci.PersistenceHelper.newQuery(
		    		pm.getExtent(org.opencrx.kernel.home1.jmi1.EMailAccount.class),
		    		userHomeSegment.refGetPath().getDescendant("userHome", ":*", "eMailAccount", ":*")
		    	);
            	emailAccountQuery.thereExistsIsActive().isTrue();
            	emailAccountQuery.name().equalTo(id);
				List<org.opencrx.kernel.home1.jmi1.EMailAccount> emailAccounts = userHomeSegment.getExtent(emailAccountQuery);
				if(emailAccounts.size() == 1) {
					org.opencrx.kernel.home1.jmi1.EMailAccount emailAccount = emailAccounts.iterator().next();
					principalName = emailAccount.refGetPath().getParent().getParent().getLastSegment().toClassicRepresentation();
					providerName = currentProviderName;
					segmentName = currentSegmentName;
					count++;
				}
				pm.close();
            }
        }
        // id is not unique --> no success
        if(count > 1) {
        	principalName = null;
        }
        pmRoot.close();
	} else {
		// Format 3: principal
		javax.jdo.PersistenceManagerFactory pmf = org.opencrx.kernel.utils.Utils.getPersistenceManagerFactory();
		javax.jdo.PersistenceManager pmRoot = pmf.getPersistenceManager(
			SecurityKeys.ROOT_PRINCIPAL, 
			null
		);			
        org.openmdx.security.realm1.jmi1.Segment realmSegment =
            (org.openmdx.security.realm1.jmi1.Segment)pmRoot.getObjectById(LOGIN_REALM_IDENTITY.getParent().getParent());
        int count = 0;
        for(org.openmdx.security.realm1.jmi1.Realm realm: realmSegment.<org.openmdx.security.realm1.jmi1.Realm>getRealm()) {
            if(!realm.refGetPath().equals(LOGIN_REALM_IDENTITY) && !"Root".equals(realm.refGetPath().getLastSegment().toClassicRepresentation())) {
           		org.openmdx.security.realm1.jmi1.Principal principal = org.opencrx.kernel.backend.SecureObject.getInstance().findPrincipal(id, realm);
           		if(principal != null && !Boolean.TRUE.equals(principal.isDisabled())) {
           			principalName = id;
           			providerName = realm.refGetPath().getSegment(2).toClassicRepresentation();
           			segmentName = realm.refGetPath().getLastSegment().toClassicRepresentation();
           			count++;
           		}
            }
		}
        // id is not unique --> no success
        if(count > 1) {
        	principalName = null;
        }
        pmRoot.close();
    }
	if(principalName != null && providerName != null && segmentName != null) {
		javax.jdo.PersistenceManagerFactory pmf = org.opencrx.kernel.utils.Utils.getPersistenceManagerFactory();
		javax.jdo.PersistenceManager pm = pmf.getPersistenceManager(
			SecurityKeys.ADMIN_PRINCIPAL + SecurityKeys.ID_SEPARATOR + segmentName, 
			null
		);
		try {
			org.opencrx.kernel.home1.jmi1.UserHome userHome = (org.opencrx.kernel.home1.jmi1.UserHome)pm.getObjectById(
				new Path("xri://@openmdx*org.opencrx.kernel.home1").getDescendant("provider", providerName, "segment", segmentName, "userHome", principalName)
			);
			pm.currentTransaction().begin();
			userHome.requestPasswordReset();
			pm.currentTransaction().commit();
			success = true;
		} catch(Exception e) {
			try {
				pm.currentTransaction().rollback();
			} catch(Exception ignore) {}
			success = false;
		}
	} else {
		success = false;
	}
}