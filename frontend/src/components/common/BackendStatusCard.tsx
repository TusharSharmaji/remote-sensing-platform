import { Card } from "../ui";
import Loading from "./Loading";
import ErrorMessage from "./ErrorMessage";

import { useHealthCheck } from "../../hooks/useHealthCheck";

function BackendStatusCard() {
  const { data, isPending, isError } = useHealthCheck();

  return (
    <Card title="Backend Connectivity">
      {isPending && <Loading />}

      {isError && (
        <ErrorMessage message="Unable to connect to backend." />
      )}

      {data && (
        <div>
          <p>
            <strong>Status:</strong> {data.status}
          </p>

          <p>
            <strong>Environment:</strong> {data.environment}
          </p>
        </div>
      )}
    </Card>
  );
}

export default BackendStatusCard;