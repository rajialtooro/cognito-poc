@Library('devops_common')_

if(env.BRANCH_NAME == "prod") {
    serviceDeployment(
        environment: 'prod',
        service: 'solution-orch-service',
    )
}
