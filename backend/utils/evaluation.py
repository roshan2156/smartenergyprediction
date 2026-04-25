import numpy as np
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score, accuracy_score, classification_report


def evaluate_regression_model(y_true, y_pred, model_name="Model"):
    """Calculate regression evaluation metrics"""
    
    mae = mean_absolute_error(y_true, y_pred)
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    r2 = r2_score(y_true, y_pred)

    mean_actual = np.mean(y_true)
    accuracy = (1 - mae / mean_actual) * 100 if mean_actual > 0 else 0

    print(f"\n📊 {model_name} Evaluation Results:")
    print("-" * 40)
    print(f"Mean Absolute Error (MAE): {mae:.4f}")
    print(f"Root Mean Square Error (RMSE): {rmse:.4f}")
    print(f"R² Score: {r2:.4f} ({r2*100:.2f}%)")
    print(f"Accuracy: {accuracy:.2f}%")
    print(f"Mean Actual Value: {mean_actual:.4f}")

    return {
        'mae': mae,
        'rmse': rmse,
        'r2': r2,
        'accuracy': accuracy,
        'mean_actual': mean_actual
    }


def evaluate_classification_model(y_true, y_pred, model_name="Model", target_names=None):
    """Calculate classification evaluation metrics"""

    accuracy = accuracy_score(y_true, y_pred)

    print(f"\n📊 {model_name} Evaluation Results:")
    print("-" * 40)
    print(f"Accuracy: {accuracy*100:.2f}%")
    print("\nClassification Report:")
    print(classification_report(y_true, y_pred, target_names=target_names))

    return {
        'accuracy': accuracy,
        'report': classification_report(y_true, y_pred, target_names=target_names)
    }


def calculate_savings(current_cost, recommended_cost):
    """Calculate savings"""

    savings = current_cost - recommended_cost
    savings_percent = (savings / current_cost) * 100 if current_cost > 0 else 0

    return {
        'amount': round(savings, 2),
        'percentage': round(savings_percent, 1)
    }


# ✅ MAIN EXECUTION (IMPORTANT 🔥)
if __name__ == "__main__":

    # 🔹 Regression Test
    y_true_reg = [10, 20, 30, 40]
    y_pred_reg = [12, 18, 29, 41]

    evaluate_regression_model(y_true_reg, y_pred_reg, "Energy Model")


    # 🔹 Classification Test
    y_true_cls = [0, 1, 1, 0]
    y_pred_cls = [0, 1, 0, 0]

    evaluate_classification_model(y_true_cls, y_pred_cls, "Waste Detection Model", target_names=["No Waste", "Waste"])


    # 🔹 Savings Test
    savings = calculate_savings(100, 80)
    print("\n💰 Savings:")
    print(savings)